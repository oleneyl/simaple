from simaple.core import ExtendedStat
from simaple.request.adapter.union_loader.adapter import get_union_artifact


def test_propensity_response(union_artifact_response):
    artifact = get_union_artifact(union_artifact_response)
    assert artifact.get_extended_stat() == ExtendedStat.model_validate(
        {
            "stat": {
                "INT_static": 150,
                "STR_static": 150,
                "DEX_static": 150,
                "LUK_static": 150,
                "attack_power": 30,
                "magic_attack": 30,
                "critical_rate": 20,
                "damage_multiplier": 15,
                "boss_damage_multiplier": 15,
                "critical_damage": 4,
                "ignored_defence": 20,
            },
            "action_stat": {"buff_duration": 20},
        }
    )