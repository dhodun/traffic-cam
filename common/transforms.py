class LogBytes(beam.DoFn):
    def process(self, element):
        import random

        # Log 1% of the time
        if random.random() < .01:
            length = len(element['bytes'])
            logging.info('[Sampled] bytes in this element: {}'.format(length))

        yield element