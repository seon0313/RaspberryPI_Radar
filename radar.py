import sys

import pygame
import time
import math
from RPi import GPIO

servo_pin = 12
trig = 16
echo = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.output(trig, False)

pygame.init()

sc = pygame.display.set_mode((800,480))
pygame.display.set_caption('Arduino Radar Viewer')
font = pygame.font.Font('font.ttf',20)

logo = pygame.image.load('tf_dot_text_logo.png')
size = logo.get_size()
scale = 2
logo = pygame.transform.scale(logo,(size[0]/scale,size[1]/scale))
logoR = logo.get_rect()
pygame.display.flip()
size = sc.get_size()
print('LOAD')
lines = {}

min_ = 3
max_ = 12.5
angle = 0
angle_step = 4
def setServo(angle_):
    if angle_ > 180 or angle_ < 0: return
    print(angle_*(max_-min_)/180)
    servo.ChangeDutyCycle(angle_*(max_-min_)/180)
    time.sleep(0.05)
servo = GPIO.PWM(servo_pin, 50)
servo.start(min_)
time.sleep(0.05)

vel = 1

while True:
    try:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        sc.fill((0,0,0))

        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        while GPIO.input(echo)==0:
            start = time.time()
        while GPIO.input(echo)==1:
            stop = time.time()
        distance = (stop-start)*34300/2
        setServo(angle)
        lines[angle] = {'d': distance, 't': time.time(), 'a':255}
        result = distance
        logoR.x = 10
        logoR.y = size[1]-logoR.h-10
        sc.blit(logo,logoR)

        angle += vel*angle_step

        if angle >= 180: vel = -1
        if angle <= 0: vel = 1
        print(angle, vel, angle_step)

        if result >= 60:
            result = f'{int(result/60)}m {result-(60*int(result/60))}'

        text = font.render(f'D: {result}cm',True, (255,255,255))
        textR = text.get_rect()
        textR.y = (size[1]/2)+230
        textR.centerx = size[0]/2
        sc.blit(text,textR)

        for i in lines.keys():
            d = lines[i]['d']
            t = lines[i]['t']
            a = lines[i]['a']


            x = (size[0]/2) + math.cos(math.radians(-i)) * 200
            y = (size[1]/2) + math.sin(math.radians(-i)) * 200
            if a>255: a = 255
            if a < 0: a = 0
            pygame.draw.line(sc,(0,a,0),(size[0]/2,size[1]/2),(x,y),3)
            x2 = (size[0] / 2) + math.cos(math.radians(-i)) * (200*((d/60)/2))
            y2 = (size[1] / 2) + math.sin(math.radians(-i)) * (200*((d/60)/2))
            pygame.draw.line(sc, (a,0,0), (x2, y2), (x, y), 3)

            lines[i]['a'] = a-5
        pygame.draw.circle(sc, (255, 255, 255), (size[0] / 2, size[1] / 2), 200, 2)
        pygame.draw.circle(sc, (100, 100, 100), (size[0] / 2, size[1] / 2), 200-((200/4)*1), 2)
        pygame.draw.circle(sc, (100, 100, 100), (size[0] / 2, size[1] / 2), 200-((200/4)*2), 2)
        pygame.draw.circle(sc, (100, 100, 100), (size[0] / 2, size[1] / 2), 200-((200/4)*3), 2)

        pygame.display.flip()
    except Exception as e: print(e)
servo.stop()
