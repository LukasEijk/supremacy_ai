# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from supremacy import helpers

# This is your team name
CREATOR = "SexDrugsAndNoPlan"


def tank_ai(tank, info, game_map):
    """
    Function to control tanks.
    """
    if not tank.stopped:
        if tank.stuck:
            tank.set_heading(np.random.random() * 360.0)
        elif "target" in info:
            tank.goto(*info["target"])


def ship_ai(ship, info, game_map):
    """
    Function to control ships.
    """
    if not ship.stopped:
        if ship.stuck:
            build_cnt = 0 
            for ind, base in enumerate(info["bases"]):
                if ship.get_distance(base.x, base.y) > 40:
                  build_cnt += 1  
                else:
                    ship.set_heading(np.random.random() * 360.0)
  
            if build_cnt == ind+1:
                ship.convert_to_base()


def jet_ai(jet, info, game_map):
    """
    Function to control jets.
    """

    if "target" in info and info["target"]:
        closest_target = min(info["target"], key=lambda target: jet.get_distance(*target))
        jet.goto(*closest_target)
 

class PlayerAi:
    """
    This is the AI bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = CREATOR  # Mandatory attribute
        self.ntanks = {}
        self.nships = {}
        # first of all create 5 b
        self.build_queue = helpers.BuildQueue(
            ["mine", "tank", "ship", "jet"], cycle=True
        )

    def run(self, t: float, dt: float, info: dict, game_map: np.ndarray):
        """
        This is the main function that will be called by the game engine.
        """

        # Get information about my team
        myinfo = info[self.team]


        # Iterate through all my bases and process build queue
        for ind, base in enumerate(myinfo["bases"]):
            # Calling the build_queue will return the object that was built by the base.
            # It will return None if the base did not have enough resources to build.
            uid = base.uid
            if uid not in self.ntanks:
                self.ntanks[uid] = 0
                self.nships[uid] = 0

            if base.mines < 3:
                if base.crystal > base.cost("mine"):
                    base.build_mine()

            elif base.mines>=2 and self.nships[uid]<=10:
                if base.crystal > base.cost("ship"):
                    base.build_ship(heading=360 * np.random.random())
                    self.nships[uid] += 1
            elif base.mines>2 :
                self.build_queue = helpers.BuildQueue(
                                [ "jet", "ship"], cycle=True)
                obj = self.build_queue(base)



        # Try to find an enemy target
        # If there are multiple teams in the info, find the first team that is not mine
        myinfo["target"] = []

        if len(info) > 1:
            for name in info:
                if name != self.team:  # Check it's not your team
                    if "bases" in info[name]:  # Target only bases
                        # Iterate over all bases and append them as tuples
                        for base in info[name]["bases"]:
                            myinfo["target"].append((base.x, base.y))

                # Control all my vehicles
        helpers.control_vehicles(
            info=myinfo, game_map=game_map, tank=tank_ai, ship=ship_ai, jet=jet_ai
        )
