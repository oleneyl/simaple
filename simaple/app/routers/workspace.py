import uuid
from typing import Any

import fastapi
import pydantic
from fastapi import Depends

from simaple.app.services.base import (
    PlayLog,
    add_play_log,
    dispatch_action,
    get_logs,
    get_workspace,
)
from simaple.core.base import ActionStat, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.simulate.base import Action
from simaple.simulate.kms import get_client
from simaple.simulate.report.base import Report
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage
from simaple.simulate.reserved_names import Tag

router = fastapi.APIRouter(prefix="/workspaces")


class WorkspaceConfiguration(pydantic.BaseModel):
    action_stat: ActionStat
    groups: list[str]
    injected_values: dict[str, Any]
    skill_levels: dict[str, int]
    v_improvements: dict[str, int]
    character_stat: Stat


class WorkspaceResponse(pydantic.BaseModel):
    id: str


@router.post("", response_model=WorkspaceResponse)
def create(
    conf: WorkspaceConfiguration,
    workspace=Depends(get_workspace),
    logs=Depends(get_logs),
) -> Any:
    workspace_id = str(uuid.uuid4())
    client = get_client(
        conf.action_stat,
        conf.groups,
        conf.injected_values,
        conf.skill_levels,
        conf.v_improvements,
    )

    damage_calculator = DPMCalculator(
        character_spec=conf.character_stat,
        damage_logic=INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
        elemental_resistance_disadvantage=0.5,
    )

    workspace[workspace_id] = {
        "client": client,
        "damage_calculator": damage_calculator,
    }

    response = PlayLog(
        events=[],
        index=0,
        validity_view={v.name: v for v in client.environment.show("validity")},
        running_view={v.name: v for v in client.environment.show("running")},
        buff_view=client.environment.show("buff"),
        clock=0,
        damage=0,
        delay=0,
        action=Action(name="*", method="elapse", payload=0),
    )

    logs[workspace_id] = [
        (
            client.environment.store.save(),
            response,
        )
    ]
    return WorkspaceResponse(id=workspace_id)


@router.post("/play/{workspace_id}", response_model=PlayLog)
def play(
    workspace_id: str,
    action: Action,
    workspaces=Depends(get_workspace),
    logs=Depends(get_logs),
) -> PlayLog:

    response = dispatch_action(workspaces[workspace_id], logs[workspace_id], action)
    add_play_log(workspaces[workspace_id], logs[workspace_id], response)

    return response


@router.get("/logs/{workspace_id}/{log_id}", response_model=PlayLog)
def get_log(
    workspace_id: str,
    log_id: int,
    workspace=Depends(get_workspace),
    logs=Depends(get_logs),
) -> PlayLog:
    current_log = logs[workspace_id]
    _, resp = current_log[log_id]

    return resp
