import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions

from google.cloud import storage

class LogBytes(beam.DoFn):
    def process(self, element):
        length = len(element)
        logging.info('bytes in this element: {}'.format(length))
        yield element

class WriteFile(beam.DoFn):
    # def setup(self):
    #     # Imports the Google Cloud client library
    #     from google.cloud import storage

    #     # Instantiates a client
    #     self.storage_client = storage.Client()



    def process(self, element):
        from google.cloud import storage
        storage_client = storage.Client()

        length = len(element)

        bucket = storage_client.bucket('dhodun1')
        blob = bucket.blob('temp/df/out-{}.jpg'.format(length))
        logging.info('Blob name: {}'.format(blob.name))
        blob.upload_from_string(element)

        
    



def run(argv=None, save_main_session=False):
    """Build and run the pipeline"""
    pipeline_options = PipelineOptions(flags=['--streaming'])
    pipeline_options.view_as(GoogleCloudOptions).project = 'dhodun1'
    pipeline_options.view_as(GoogleCloudOptions).temp_location = 'gs://dhodun1/temp/job'
    pipeline_options.view_as(GoogleCloudOptions).staging_location = 'gs://dhodun1/temp/df/staging'
    pipeline_options.view_as(GoogleCloudOptions).region = 'us-central1'
    # pipeline_options.view_as(SetupOptions).streaming = True
    # pipeline_options.view_as(SetupOptions).requirements_file = 'requirements.txt'
    pipeline_options.view_as(SetupOptions).setup_file = '/Users/dhodun/developer/traffic-cam/setup.py'
    with beam.Pipeline(options=pipeline_options, runner='dataflow') as p:

        topic = 'projects/dhodun1/topics/test_traffic_topic'

        messages = ( p 
            | 'readFromPubSub' >> beam.io.ReadFromPubSub(topic=topic)
            | 'CountBytes' >> beam.ParDo(LogBytes())
            | 'WriteToGCS' >> beam.ParDo(WriteFile())
        )

        # output = ( messages
        #     | 'writeToGCS' >> beam.ParDo(WriteFile())
        
        # )



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
