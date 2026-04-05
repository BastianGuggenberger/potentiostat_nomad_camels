from pathlib import Path
import sys
import math

#importing packages:
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import xyz_stage
import head_control
#import solution_mixing


class sample():

    def __init__(self):
        
        self.params = {}
        self.params["SAMPLE_HEIGHT"] = 1.0 #mm, mm
        self.params["SAMPLE_DISTANCEBORDER"] = 5.0 #mm, mm
        self.params["SAMPLE_ORIGIN"] = (20.5, 68.5) # mm, mm
        self.params["ORIGIN_OFFSET"] = (0., 0.) # mm, mm
        self.params["SAMPLE_SIZE"] = (25.0, 25.0) # mm, mm
        self.params["MOVE_HEIGHT"] = 30.0 # mm
        self.params["SAFE_HEIGHT"] = 80.0 # mm
        self.params["MIXER_LIMIT"] = (125.0, 125.0) # mm, mm
        self.params["MIXER_HEIGHT"] = 62.0 # mm
        self.params["MIXER_POSITION"] = (181.7, 73.5) # mm, mm
        self.params["RESERVOIR_HEIGHT"] = 3.0 # mm
        self.params["RESERVOIR_POSITION"] = (205.0, 193.0) # mm, mm
        self.params["CLEANING_HEIGHT"] = 3.0 # mm
        self.params["CLEANING_POSITION"] = (156.0, 193.0) # mm, mm
        self.params["WASTE_HEIGHT"] = 27.5 # mm
        self.params["WASTE_POSITION"] = (205.0, 144.0) # mm, mm

        self.params["SHED_DROP_DISTANCE"] = 25.0 # mm
        self.params["TOTAL_VOLUME"] = 1.0 # mL
        self.params["MEASUREMENT_VOLUME"] = 0.5 # ml
        self.params["NEGATIVE_VOLUME"] = 0.15 # ml
        self.params["MIXER_VOLUME"] = 2.0 # ml
        self.params["PURGE_VOLUME"] = 0.5 # mL
        self.params["CLEANING_VOLUME"] = 1.0 # mL
        self.params["CLEANING_STEPS"] = 3 # -
        self.params["TARGET_GRAM_FORCE"] = 60.0 # gf

        #for testing:
        self.params["COPPER"] = (40.0, 130.0)

        #calculate sample points

        self.samplepoints = []

            
    def createsamplepointsbynumber(self, pointnumber):
        self.samplepoints = [] #clear previous points

        pointsperrow = math.ceil(math.sqrt(pointnumber)) #round up
        distance = (self.params["SAMPLE_SIZE"][0]-2*self.params["SAMPLE_DISTANCEBORDER"])/(pointsperrow-1)
        
        #relative positions:
        producedpoints = 0
        y = self.params["SAMPLE_DISTANCEBORDER"]
        while(y<=self.params["SAMPLE_SIZE"][0]-self.params["SAMPLE_DISTANCEBORDER"]):
            x = self.params["SAMPLE_DISTANCEBORDER"]
            while(x<=self.params["SAMPLE_SIZE"][1]-self.params["SAMPLE_DISTANCEBORDER"]):
                if (producedpoints<pointnumber):
                    self.samplepoints.append((x,y))
                    producedpoints += 1
                else:
                    break
                x += distance
            y += distance

        #convert to absolute positions:
        self.samplepoints = [(x+self.params["SAMPLE_ORIGIN"][0]+self.params["ORIGIN_OFFSET"][0],
                            y+self.params["SAMPLE_ORIGIN"][1]+self.params["ORIGIN_OFFSET"][1]) for (x,y) in self.samplepoints]

        #print(self.samplepoints)
        
        string = ""
        first = True
        for point in self.samplepoints:
            if first == False:
                string += ";"
            first = False
            string += str(point[0])
            string += ","
            string += str(point[1])

        print(string)


SAMPLE_ORIGIN = (20.5, 68.5) # mm, mm
ORIGIN_OFFSET = (0., 0.) # mm, mm
SAMPLE_SIZE = (25.0, 25.0) # mm, mm
MOVE_HEIGHT = 30.0 # mm
SAFE_HEIGHT = 80.0 # mm
MIXER_LIMIT = (125.0, 125.0) # mm, mm
MIXER_HEIGHT = 62.0 # mm
MIXER_POSITION = (181.7, 73.5) # mm, mm
RESERVOIR_HEIGHT = 3.0 # mm
RESERVOIR_POSITION = (205.0, 193.0) # mm, mm
CLEANING_HEIGHT = 3.0 # mm
CLEANING_POSITION = (156.0, 193.0) # mm, mm
WASTE_HEIGHT = 27.5 # mm
WASTE_POSITION = (205.0, 144.0) # mm, mm
SHED_DROP_DISTANCE = 25.0 # mm
TOTAL_VOLUME = 1.0 # mL
MEASUREMENT_VOLUME = 0.5 # ml
NEGATIVE_VOLUME = 0.15 # ml
MIXER_VOLUME = 2.0 # ml
PURGE_VOLUME = 0.5 # mL
CLEANING_VOLUME = 1.0 # mL
CLEANING_STEPS = 3 # -
TARGET_GRAM_FORCE = 60.0 # gf

# xyz_stage.connect()
# head_control.hardware.connect()
# solution_mixing.hardware.connect()


def safe_move(stage,
              position: tuple[float, float],
              move_height: float = MOVE_HEIGHT,
              mixer_limit: tuple[float, float] = MIXER_LIMIT,
              safe_height: float = SAFE_HEIGHT) -> None:
    current_position = stage.current_position()
    if ((position[0] > mixer_limit[0] and position[1] < mixer_limit[1])
            or (current_position['X'] > mixer_limit[0] and current_position['Y'] < mixer_limit[1])):
        stage.height(safe_height)
    else:
        stage.height(move_height)
        if position[0] > mixer_limit[0] and current_position['Y'] < mixer_limit[1]:
            stage.position(current_position['X'], mixer_limit[1], fast=True)
        if position[1] < mixer_limit[1] and current_position['X'] > mixer_limit[0]:
            stage.position(mixer_limit[0], current_position['Y'], fast=True)
    stage.position(*position, fast=True)

def draw_solution_finalize(stage,
                           head,
                           measurement_volume: float = MEASUREMENT_VOLUME,
                           cleaning_position: tuple[float, float] = CLEANING_POSITION,
                           cleaning_height: float = CLEANING_HEIGHT,
                           waste_position: tuple[float, float] = WASTE_POSITION,
                           waste_height: float = WASTE_HEIGHT,
                           negative_volume: float = NEGATIVE_VOLUME,
                           shed_drop_distance: float = SHED_DROP_DISTANCE,
                           final_height: float = MOVE_HEIGHT) -> None:
    safe_move(stage,cleaning_position)
    stage.height(cleaning_height)
    safe_move(stage,waste_position)
    stage.height(waste_height)
    head.fill_head(measurement_volume)
    head.change_volume(negative_volume)
    stage.position(-shed_drop_distance, 0., relative=True, fast=True)
    stage.height(final_height)

def draw_solution_reservoir(stage,
                            head,
                            measurement_volume: float = MEASUREMENT_VOLUME,
                            total_volume: float = TOTAL_VOLUME,
                            reservoir_position: tuple[float, float] = RESERVOIR_POSITION,
                            reservoir_height: float = RESERVOIR_HEIGHT,
                            **kwargs) -> None:
    safe_move(stage,reservoir_position)
    stage.height(reservoir_height)
    head.fill_head(total_volume)
    draw_solution_finalize(stage,head,measurement_volume, **kwargs)

"""
def draw_solution_mixer(stage,
                        head,
                        ratios: tuple[float, float, float],
                        measurement_volume: float = MEASUREMENT_VOLUME,
                        total_volume: float = TOTAL_VOLUME,
                        mixer_position: tuple[float, float] = MIXER_POSITION,
                        mixer_height: float = MIXER_HEIGHT,
                        **kwargs) -> None:
    safe_move(stage,mixer_position)
    stage.height(mixer_height)
    solution_mixing.liquid_handling.mix_solution(*ratios)
    head.fill_head(total_volume)
    solution_mixing.liquid_handling.discard_solution()
    draw_solution_finalize(stage,head,measurement_volume, **kwargs)
"""

def discard_solution(stage,
                     head,
                     purge_volume: float = PURGE_VOLUME,
                     waste_position: tuple[float, float] = WASTE_POSITION,
                     waste_height: float = WASTE_HEIGHT,
                     final_height: float = MOVE_HEIGHT,
                     negative_volume: float = NEGATIVE_VOLUME) -> None:
    head.change_volume(negative_volume)
    safe_move(stage,waste_position)
    stage.height(waste_height)
    head.purge_head(purge_volume)
    stage.height(final_height)

def clean_head(stage,
               head,
               cleaning_volume: float = CLEANING_VOLUME,
               cleaning_steps: int = CLEANING_STEPS,
               cleaning_position: tuple[float, float] = CLEANING_POSITION,
               cleaning_height: float = CLEANING_HEIGHT,
               purge_volume: float = PURGE_VOLUME,
               waste_position: tuple[float, float] = WASTE_POSITION,
               waste_height: float = WASTE_HEIGHT,
               final_height: float = MOVE_HEIGHT) -> None:
    for i in range(cleaning_steps):
        safe_move(stage,cleaning_position)
        stage.height(cleaning_height)
        head.fill_head(cleaning_volume)
        discard_solution(stage,head,purge_volume, waste_position, waste_height, final_height, 0)

def approach_sample(stage,
                    head,
                    position: tuple[float, float],
                    sample_height: float,
                    target_gram_force: float = TARGET_GRAM_FORCE,
                    sample_origin: tuple[float, float] = SAMPLE_ORIGIN,
                    origin_offset: tuple[float, float] = ORIGIN_OFFSET,
                    move_height: float = MOVE_HEIGHT) -> None:
    absolute_position = (sample_origin[0] + position[0] + origin_offset[0], sample_origin[1] + position[1] + origin_offset[1])
    safe_move(stage,absolute_position, move_height=move_height)
    stage.height(sample_height + 1.0)
    head.approach(stage, target_gram_force)
