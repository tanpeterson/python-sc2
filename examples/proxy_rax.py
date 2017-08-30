import random

import sc2
from sc2 import Race, Difficulty, ActionResult
from sc2.constants import *
from sc2.player import Bot, Computer

class ProxyRaxBot(sc2.BotAI):
    async def on_step(self, state, iteration):
        cc = self.units(COMMANDCENTER)
        if not cc.exists:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for unit in self.workers | self.units(MARINE):
                await self.do(unit.attack(target))
            return
        else:
            cc = cc.first

        if self.units(MARINE).idle.amount > 15 and iteration % 50 == 1:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for marine in self.units(MARINE).idle:
                await self.do(marine.attack(target))

        if self.can_afford(SCV) and self.workers.amount + len(cc.orders) < 16:
            await self.do(cc.train(SCV))

        elif self.supply_left < 2:
            if self.can_afford(SUPPLYDEPOT):
                await self.build(SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))

        elif self.units(BARRACKS).amount < 3 or self.minerals > 500:
            if self.can_afford(BARRACKS):
                p = self.game_info.map_center.towards(self.enemy_start_locations[0], 25)
                await self.build(BARRACKS, near=p)

        if self.can_afford(MARINE) and self.units(BARRACKS).ready.exists:
            await self.do(self.units(BARRACKS).ready.random.train(MARINE))

        for scv in self.units(SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))

def main():
    sc2.run_game(sc2.maps.get("Sequencer LE"), [
        Bot(Race.Terran, ProxyRaxBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=True)

if __name__ == '__main__':
    main()
