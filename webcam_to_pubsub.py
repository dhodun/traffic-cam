import time

import cv2
from google.cloud import pubsub_v1
from imutils.video.fps import FPS
from imutils.video.webcamvideostream import WebcamVideoStream
import os

# VideoStream
stream = WebcamVideoStream(src=0).start()
time.sleep(2.0)

fps = FPS().start()

# Setup PubSub
client = pubsub_v1.PublisherClient.from_service_account_file('/home/pi/service_account.json')

PROJECT_ID = 'dhodun1'
TOPIC_NAME = 'test_traffic_topic'

topic_name = client.topic_path(PROJECT_ID, TOPIC_NAME)
project = client.project_path(PROJECT_ID)

# See if topic created
topics = []
for topic in client.list_topics(project):
    # Because GRPC iterator
    topics.append(topic.name)

if topic_name not in topics:
    print('Creating PubSub topic "{}"'.format(topic_name))
    client.create_topic(topic_name)
else:
    print('PubSub topic "{}" already created'.format(topic_name))




# Main loop
while True:

    # Process a frame
    frame = stream.read()

    # Increment counter
    fps.update()
    fps.stop()
    
    cv2.putText(frame, "FPS: {}".format(fps.fps()),
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0))

    cv2.imshow("Video", frame)
    _, buffer = cv2.imencode('.jpg', frame)
    future = client.publish(topic_name, buffer.tostring())
    message_id = future.result()

    # Check to see if 'q' is pressed to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cv2.destroyAllWindows()
stream.stop()
