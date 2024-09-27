from simaple.request.application.base import Token, get_character_id


async def compute_character(
    character_name: str,
    token: Token,
):
    character_id = await get_character_id(token, character_name)

    async def ability_stat(self): ...

    async def propensity(self): ...

    async def doping(self): ...

    def passive(self): ...

    def default_extended_stat(self): ...

    def gearset(self): ...

    def hyperstat(self): ...

    def links(self): ...

    def union_squad(self): ...

    def union_occupation(self): ...

    def artifact(self): ...

    def level(self): ...

    def level_stat(self): ...
