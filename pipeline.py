import datetime
import logging

import apache_beam as beam

LABELS_TO_DETECT = ['Car', 'Truck']
THRESHOLD = 0.90

class AddMetadata(beam.DoFn):
    def process(self, element, event_timestamp=beam.DoFn.TimestampParam):
        import random
        import string

        timestamp_string = event_timestamp.to_utc_datetime().strftime("%Y-%m-%d_%H-%M-%S-%U")

        length = len(element)

        # Added random string since every frame in bundle was getting same frame name during testing phase
        random_string = ''.join(
            [random.choice(string.ascii_letters + string.digits) for n in range(8)])
        blob_name = 'temp/df/out-{}-bytes-{}-rand-{}.jpg'.format(
            timestamp_string, length, random_string)
        frame_path = f'gs://dhodun1/{blob_name}'

        yield {'bytes': element, 'blob_name': blob_name,
               'frame_path': frame_path, 'event_timestamp': event_timestamp.to_rfc3339()}


class AnnotateFrames(beam.DoFn):

    def setup(self):
        # Imports the Google Cloud client library
        # Initiate client in setup for re-use across bundles
        # Works on DirectRunner as of 2.22.0

        from google.cloud import vision
        from google.cloud.vision import types
        
        logging.info('AnnotateFrames setup called')

        # Instantiates a client
        self.image_client = vision.ImageAnnotatorClient()


    def process(self, element):
        # Perform label detection
        response = self.image_client.label_detection({'content': element['bytes']})
        

        labels = response.label_annotations

        is_car = False
        for label in labels:
            print(label)
            if label.description in LABELS_TO_DETECT:
                if label.score > THRESHOLD:
                    is_car = True
        
        # Add to element dict
        element['labels'] = repr(labels)
        element['is_car'] = is_car

        yield element

class FilterForBQ(beam.DoFn):
    def process(self, element):
        bq_data = {}
        bq_data['frame_path'] = element['frame_path']
        bq_data['event_timestamp'] = element['event_timestamp']
        bq_data['is_car'] = element['is_car']
        bq_data['labels'] = element['labels']

        yield bq_data


class WriteFile(beam.DoFn):

    def setup(self):
        # Imports the Google Cloud client library
        # Initiate client in setup for re-use across bundles
        # Doesn't work with DirectRunner yet      
        from google.cloud import storage

        logging.info('WriteFile setup called')

        # Instantiates a client
        self.storage_client = storage.Client()

    def process(self, element, event_timestamp=beam.DoFn.TimestampParam):
        import random
        
        # TODO: un-hard-code bucket
        bucket = self.storage_client.bucket('dhodun1')
        blob = bucket.blob(
            element['blob_name'])

        if random.random() < 0.01:
            logging.info(f"File path:{element['frame_path']}")
        blob.upload_from_string(element['bytes'])


class LogBytes(beam.DoFn):
    def process(self, element):
        import random

        # Log 1% of the time
        if random.random() < .01:
            length = len(element['bytes'])
            logging.info('[Sampled] bytes in this element: {}'.format(length))

        yield element


def run_camera_pipeline(argv=None, save_main_session=False, in_test_mode=True, update_job_name=None):
    """Build and run the pipeline"""
    import shutil
    import os
    import subprocess

    job_name = 'autoscale-random-traffic-cam' + '-' + datetime.datetime.now().strftime('%y%m%d-%H%M%S')

    if in_test_mode:
        print('Launching local job ... hang on')
        OUTPUT_DIR = './camera_pipeline'
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
        os.makedirs(OUTPUT_DIR)
    else:
        print('Launching DataFlow job {} .... hang on'.format(job_name))
        OUTPUT_DIR = 'gs://{}/camera_pipeline'.format(BUCKET)
        
        try:
            # TODO: This interferes with existing job, it can't shut down properly because the staging files disappear
            # subprocess.check_call('gsutil -m rm -r {}'.format(OUTPUT_DIR).split())
            pass
        except:
            pass

    options = {
        'save_main_session': True,
        'project': PROJECT,
        'region': REGION,
        # 'requirements_file': 'requirements.txt',
        'setup_file': './setup.py',
        'streaming': True,
        'temp_location': os.path.join(OUTPUT_DIR, 'tmp', job_name),
        'staging_location': os.path.join(OUTPUT_DIR, 'tmp', job_name, 'staging'),
        'job_name': job_name,
        # 'num_workers': 1,
        'autoscaling_algorithm': 'THROUGHPUT_BASED',
        'max_num_workers': 5,
        
    }

    if update_job_name is not None:
        options['job_name'] = update_job_name
        options['update'] = True


    opts = beam.pipeline.PipelineOptions(flags=[], **options)
    if in_test_mode:
        RUNNER = 'DirectRunner'
    else:
        RUNNER = 'DataflowRunner'
    with beam.Pipeline(RUNNER, options=opts) as p:

        # topic = 'projects/dhodun1/topics/test_traffic_topic'
        subscription = 'projects/dhodun1/subscriptions/streaming_dataflow_sub'

        #TODO: Add branching pipeline for GCS

        # Initial frame ingestiong
        frames = (p
                    | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription=subscription, timestamp_attribute='event_timestamp')
                    | 'AddMetadata' >> beam.ParDo(AddMetadata())
                    )

        # Write historical images to GCS coldline for later processing
        _ = (
                    frames
                    | 'CountBytes' >> beam.ParDo(LogBytes())
                    | 'WriteToGCS' >> beam.ParDo(WriteFile())
                    )

        # Annotate image via Vision API and copy metadata to BigQuery
        _ = (
                    frames
                    | 'AnnotateFrames' >> beam.ParDo(AnnotateFrames())
                    | 'FilterBQData' >> beam.ParDo(FilterForBQ())
                    | 'RecordInBQ' >> beam.io.WriteToBigQuery('dhodun1:traffic_cam.frames',
                    schema='frame_path:STRING,event_timestamp:TIMESTAMP', write_disposition='WRITE_APPEND')
                    )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    PROJECT = 'dhodun1'
    REGION = 'us-central1'
    BUCKET = 'dhodun1'

    run_camera_pipeline(in_test_mode=False
    , update_job_name='autoscale-random-traffic-cam-200901-235357'
    )
