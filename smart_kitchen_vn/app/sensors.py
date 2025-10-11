import asyncio, random, time
class Sensor:
    def __init__(self,name,interval=1.0): self.name=name; self.interval=interval
    async def run(self,out_queue:'asyncio.Queue'):
        while True:
            data=self.read(); ts=time.time(); await out_queue.put({'sensor':self.name,'time':ts,'data':data}); await asyncio.sleep(self.interval)
    def read(self): raise NotImplementedError
class GasSensorMQ2(Sensor):
    def read(self):
        base=random.uniform(10,80)
        if random.random()<0.03:
            spike=random.uniform(210,600); value=base+spike
        else: value=base
        return {'ppm':round(value,2)}
class GasSensorMQ5(Sensor):
    def read(self):
        base=random.uniform(5,60)
        if random.random()<0.02:
            spike=random.uniform(160,450); value=base+spike
        else: value=base
        return {'ppm':round(value,2)}
class SmokeTempSensor(Sensor):
    def read(self):
        smoke=random.gauss(5,5); temp=random.gauss(28,3)
        if random.random()<0.01:
            smoke+=random.uniform(60,120); temp+=random.uniform(30,80)
        smoke=max(0,min(200,smoke)); temp=max(-10,min(400,temp)); return {'smoke':round(smoke,1),'temp_c':round(temp,1)}
class TempHumiditySensor(Sensor):
    def read(self): temp=random.gauss(6,3); humidity=random.gauss(55,10); return {'temp_c':round(temp,1),'humidity':round(max(0,min(100,humidity)),1)}
class MotionLightSensor(Sensor):
    def read(self):
        motion=random.random()<0.2; base_lux=random.uniform(50,400)
        if motion and random.random()<0.5: base_lux+=random.uniform(0,100)
        if random.random()<0.05: base_lux=random.uniform(0,30)
        return {'motion':motion,'lux':round(base_lux,1)}
class WaterFlowSensor(Sensor):
    def read(self):
        if random.random()<0.08: flow=random.uniform(1.0,6.0)
        elif random.random()<0.01: flow=random.uniform(0.2,0.8)
        else: flow=0.0
        return {'lpm':round(flow,2)}
