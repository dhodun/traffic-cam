import argparse
import datetime
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

from google.cloud import storage


class LogBytes(beam.DoFn):
    def process(self, element):
        import random

        # Log 1% of the time
        if random.random() < .01:
            length = len(element)
            logging.info('[Sampled] bytes in this element: {}'.format(length))

        yield element


class WriteFile(beam.DoFn):
    
    # def setup(self):
    #     # Imports the Google Cloud client library
    #     from google.cloud import storage

    #     logging.info('WriteFile setup called')

    #     # Instantiates a client
    #     self.storage_client = storage.Client()

    def process(self, element):
        from google.cloud import storage
        import datetime
        import random
        import os
        import binascii

        now = datetime.datetime.now()

        storage_client = storage.Client()

        length = len(element)

        bucket = storage_client.bucket('dhodun1')
        # TODO: Change this, since it names every image in a bundle the same and overwrites?
        blob = bucket.blob(
            'temp/df/out-{}-bytes-{}-rand-{}.jpg'.format(now.strftime("%Y-%m-%d_%H-%M-%S-%U"), length, binascii.hexlify(os.urandom(8))))
        if random.random() < 0.01:
            logging.info('Blob name: {}'.format(blob.name))
        blob.upload_from_string(element)


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
            # TODO: Does this interfere with updating a streaming job that exists?
            subprocess.check_call('gsutil -m rm -r {}'.format(OUTPUT_DIR).split())
        except:
            pass

    # TODO: staging is causing conflicts with existing job sometimes?
    options = {
        'save_main_session': False,
        'project': PROJECT,
        'region': REGION,
        'requirements_file': 'requirements.txt',
        'streaming': True,
        'temp_location': os.path.join(OUTPUT_DIR, 'tmp', job_name),
        'staging_location': os.path.join(OUTPUT_DIR, 'tmp', job_name, 'staging'),
        'job_name': job_name,
        # 'num_workers': 1,
        'autoscaling_algorithm': 'THROUGHPUT_BASED',
        'max_num_workers': 400,
        
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

        topic = 'projects/dhodun1/topics/test_traffic_topic'
        subscription = 'projects/dhodun1/subscriptions/streaming_dataflow_sub'

        messages = (p
                    # TODO: consider switching to subscription?
                    | 'readFromPubSub' >> beam.io.ReadFromPubSub(subscription=subscription)
                    # | 'readFromPubSub' >> beam.io.ReadFromPubSub(topic=topic)
                    | 'CountBytes' >> beam.ParDo(LogBytes())
                    | 'WriteToGCS' >> beam.ParDo(WriteFile())
                    )

        # output = ( messages
        #     | 'writeToGCS' >> beam.ParDo(WriteFile())

        # )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    PROJECT = 'dhodun1'
    REGION = 'us-central1'
    BUCKET = 'dhodun1'

    # run_camera_pipeline(in_test_mode=True)
    run_camera_pipeline(in_test_mode=False)
    # , update_job_name='beamapp-dhodun-0426182249-193910'
