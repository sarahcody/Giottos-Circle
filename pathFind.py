import matplotlib.pyplot as plt
import math
import paho.mqtt.client as mqtt
import time
import numpy as np

# defines x and y coordinates in a circle given the diameter & number of points requested
def makeCircle(diameter, points):
    if points < 5:
        print('Need at least 5 points')

    x = []  # Establishes array of x values
    y = []  # ^^

    for i in range(points):
        angle = 2*math.pi*i/points
        x_curr = diameter/2*math.cos(angle)
        y_curr = diameter/2*math.sin(angle)

        x.append(x_curr)
        y.append(y_curr)
    return x, y

# finds angles needed to draw the circle
def findPath(x, y, arm_l):
    theta1 = []
    theta2 = []
    x0, y0 = 0, 0  # Initial position of the first joint (base)
    x1, y1 = [], []  # Positions of the second joint
    x2, y2 = [], []

    for i in range(len(x)):
        x0, y0 = 0, 0  # Initial position of the first joint (base)
        x1, y1 = [], []  # Positions of the second joint
        x2, y2 = [], [] # End position

        # Calculates theta1
        beta = math.atan2(y[i], x[i])
        l_diag = math.sqrt((x[i]**2)+(y[i]**2))
        cos_alpha = (l_diag**2/(2*arm_l*l_diag))
        alpha = math.atan2(math.sqrt(1-((cos_alpha)**2)), cos_alpha)
        theta1_curr = alpha + beta

        d = math.sqrt(x[i]**2 + y[i]**2)
        gamma = math.acos((d**2 - 2 * arm_l**2) / (-2 * arm_l**2))

        # Calculate theta2
        theta2_curr = math.pi - gamma

        theta1.append(theta1_curr)
        theta2.append(theta2_curr)

        x1_curr = x0 + arm_l * math.cos(theta1_curr)
        y1_curr = y0 + arm_l * math.sin(theta1_curr)
        x2_curr = x0 + d * math.cos(theta1_curr + theta2_curr)
        y2_curr = y0 + d * math.sin(theta1_curr + theta2_curr)

        x1.append(x1_curr)
        y1.append(y1_curr)
        x2.append(x2_curr)
        y2.append(y2_curr)

    return x1, y1, x2, y2, theta1, theta2

x, y = makeCircle(1, 10)
x1, y1, x2, y2, theta1, theta2 = findPath(x, y, 1)

plt.figure(figsize=(8, 8))
plt.plot(x, y, 'ro', label='Desired Path')
plt.axis('equal')
plt.show()


broker_address='67.253.32.232'

def callback(source,user,message):
    print(message.payload.decode())

client = mqtt.Client("sarahc")
client.on_message = callback

client.connect(broker_address)
client.loop_start()
client.subscribe('ME035')

for i in range(len(theta1)):
    theta1i = theta1[i]
    theta2i = theta2[i]
    message = '('+str(np.rad2deg(theta1i))+','+str(np.rad2deg(theta2i))+')'
    print(message)
    client.publish("ME035", message)
    time.sleep(0.01)

client.loop_stop()
client.disconnect()
