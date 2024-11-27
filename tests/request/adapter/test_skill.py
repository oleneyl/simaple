import pytest

from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.request.adapter.skill_loader._converter import (
    _get_passive_skill_effect_from_description,
    get_combat_power_related_stat,
    compute_hexa_stat,
    compute_passive_skill_stat,
    get_zero_order_skill_effect,
)


def test_passive_fetch(skill_aggregated_response):
    passive_stat = compute_passive_skill_stat(
        skill_aggregated_response, character_level=284
    )
    assert passive_stat.model_dump() == {
        "stat": {
            "STR": 0.0,
            "LUK": 0.0,
            "INT": 255.0,
            "DEX": 0.0,
            "STR_multiplier": 0.0,
            "LUK_multiplier": 0.0,
            "INT_multiplier": 0.0,
            "DEX_multiplier": 0.0,
            "STR_static": 0.0,
            "LUK_static": 0.0,
            "INT_static": 0.0,
            "DEX_static": 0.0,
            "attack_power": 20.0,
            "magic_attack": 63.0,
            "attack_power_multiplier": 0.0,
            "magic_attack_multiplier": 0.0,
            "critical_rate": 30.0,
            "critical_damage": 13.0,
            "boss_damage_multiplier": 0.0,
            "damage_multiplier": 50.0,
            "final_damage_multiplier": 40.0,
            "ignored_defence": 20.0,
            "MHP": 475.0,
            "MMP": 475.0,
            "MHP_multiplier": 0.0,
            "MMP_multiplier": 0.0,
            "elemental_resistance": 10.0,
        },
        "action_stat": {
            "cooltime_reduce": 0.0,
            "summon_duration": 0.0,
            "buff_duration": 55.0,
            "cooltime_reduce_rate": 0.0,
        },
        "level_stat": {
            "STR": 0.0,
            "LUK": 0.0,
            "INT": 0.0,
            "DEX": 0.0,
            "attack_power": 0.0,
            "magic_attack": 0.0,
        },
    }


def test_hexa_stat(hexa_stat_response):
    assert compute_hexa_stat(hexa_stat_response).get_stat() == Stat(
        magic_attack=60,
        critical_damage=5.6,
        boss_damage_multiplier=17,
    )


def test_hexa_stat_with_main_stat(hexa_stat_response_2):
    assert compute_hexa_stat(hexa_stat_response_2).get_stat() == Stat(
        magic_attack=30,
        critical_damage=1.4,
        INT_static=1000,
    )


def test_get_passive_effect(skill_0_response):
    zero_order_passive_effect, liberated = get_zero_order_skill_effect(skill_0_response)
    assert zero_order_passive_effect == ExtendedStat(
        stat=Stat(
            STR=5 + 10,
            DEX=5 + 10,
            INT=5 + 10,
            LUK=5 + 10,
            attack_power=5 + 10 + 30 + (8 + 7 + 7),
            magic_attack=5 + 10 + 30 + (8 + 7 + 7),
            final_damage_multiplier=10,
            boss_damage_multiplier=35,
            ignored_defence=35,
        ),
        action_stat=ActionStat(buff_duration=15),
    )
    assert liberated is True


def test_get_combat_power_related_stat(skill_0_response):
    zero_order_passive_effect, liberated = get_combat_power_related_stat(skill_0_response)
    assert zero_order_passive_effect == ExtendedStat(
        stat=Stat(
            STR=5 + 10,
            DEX=5 + 10,
            INT=5 + 10,
            LUK=5 + 10,
            attack_power=5 + 10 + 30 + (8 + 7 + 7),
            magic_attack=5 + 10 + 30 + (8 + 7 + 7),
            final_damage_multiplier=10,
            boss_damage_multiplier=35,
            ignored_defence=35,
        ),
        action_stat=ActionStat(buff_duration=15),
    )
    assert liberated is True


@pytest.mark.parametrize(
    "skill_effect, expected",
    [
        (
            {
                "skill_name": "달팽이 세마리",
                "skill_description": "[마스터 레벨 : 3]\n달팽이 껍질을 던져 원거리의 적을 공격한다.",
                "skill_level": 2,
                "skill_effect": "MP 5 소비하여 데미지 25",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBMA.png",
                "skill_effect_next": "MP 7 소비하여 데미지 40",
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "회복",
                "skill_description": "[마스터 레벨 : 3]\n자신의 HP를 30초 동안 지속적으로 회복시킨다. \n재사용 대기시간 : 2분",
                "skill_level": 1,
                "skill_effect": "MP 5 소비하여 30초 동안 HP 24 회복",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBMB.png",
                "skill_effect_next": "MP 10 소비하여 30초 동안 HP 48 회복",
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "민첩한 몸놀림",
                "skill_description": "[마스터 레벨 : 3]\n순간적으로 빠르게 이동한다. \n재사용 대기시간 : 1분",
                "skill_level": 3,
                "skill_effect": "MP 10 소비하여 12초 동안 이동속도 20 증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBMC.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "장인의 혼",
                "skill_description": "[마스터 레벨 : 1]\n장인의 혼을 빌려 착용할 수 없는 아이템에도 주문서를 사용할 수 있다.",
                "skill_level": 1,
                "skill_effect": None,
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBMD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "영웅의 메아리",
                "skill_description": "[마스터 레벨 : 1]\n주변 모든 캐릭터의 공격력과 마력을 증가시킨다.",
                "skill_level": 1,
                "skill_effect": "MP 30 소비하여 2400초 동안 공격력, 마력 4% 증가\n재사용 대기시간 300초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBMF.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "정령의 축복",
                "skill_description": "[마스터 레벨 : 20]\r\n다른 캐릭터를 레벨 10이상 육성하면 스킬포인트 1이 증가한다. 단, 정령의 축복과 여제의 축복중 좋은 효과로 발동된다.",
                "skill_level": 20,
                "skill_effect": "공격력 20, 마력 20 증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHOBNC.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(attack_power=20, magic_attack=20)),
        ),
        (
            {
                "skill_name": "플라잉",
                "skill_description": "[마스터 레벨 : 1]\n용족의 신비한 힘을 사용해 하늘을 난다. 단, 추락시 받는 낙하 데미지가 매우 크다.\n발동할 때 MP 90 소비.",
                "skill_level": 1,
                "skill_effect": None,
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBOG.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "여제의 축복",
                "skill_description": "[마스터 레벨 : 30]\r\n다른 시그너스 캐릭터와 미하일 캐릭터를 레벨 5이상 육성하면 스킬포인트 1이 증가한다. 단, 정령의 축복과 여제의 축복중 높은 효과로 발동된다.\r\n다른 시그너스, 미하일 캐릭터의 고귀한 정신에 의해 마스터 레벨이 최대 30까지 확장될 수 있다.",
                "skill_level": 30,
                "skill_effect": "공격력 30, 마력 30 증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHOBLD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(attack_power=30, magic_attack=30)),
        ),
        (
            {
                "skill_name": "오즈의 플레임 기어",
                "skill_description": "[마스터 레벨 : 5]\r\n소환된 오즈가 일정 시간 동안 자신의 주변에 불의 장막을 친다. 장막 내에 있는 몬스터는 일정 확률로 발화 상태가 되어 도트 데미지를 입는다. 특정 레벨이 오를때 마다 스킬 레벨 1을 올릴 수 있다.",
                "skill_level": 5,
                "skill_effect": "MP 35 소비, 15초 동안 280% 데미지의 불의 장막 생성, 발화 시 5초 동안 1초 당 130%의 도트 데미지",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPBLG.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "여제의 강화",
                "skill_description": "[마스터 레벨 : 1]\r\n자신의 레벨 보다 높은 아이템을 장착할 수 있다.",
                "skill_level": 1,
                "skill_effect": "10 레벨 높은 아이템 장착가능",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHOBEA.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "연합의 의지",
                "skill_description": "[마스터 레벨 : 1]\r\n연합의 의지에 따라 강한 힘을 발휘한다.",
                "skill_level": 1,
                "skill_effect": "영구적으로 힘 5, 민첩 5, 지능 5, 행운 5, 공격력 5, 마력 5 증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHOAFA.png",
                "skill_effect_next": None,
            },
            ExtendedStat(
                stat=Stat(STR=5, DEX=5, INT=5, LUK=5, attack_power=5, magic_attack=5)
            ),
        ),
        (
            {
                "skill_name": "링크 매니지먼트",
                "skill_description": "[마스터 레벨 : 1]\r\n월드 내 다른 캐릭터의 링크 스킬을 전수 받거나 현재 전수 받고 있는 링크 스킬을 해제할 수 있다.",
                "skill_level": 1,
                "skill_effect": "자신의 링크 스킬 전수 상태를 관리",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPDJB.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "리턴 투 메이플",
                "skill_description": "[마스터 레벨 : 1]\r\n메이플 아일랜드로 돌아간다.",
                "skill_level": 1,
                "skill_effect": "사용 시 메이플 아일랜드의 사우스페리 항구로 귀환.\n재사용 대기시간 600초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFPCLHPDEB.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "루나 드림 Lv.1",
                "skill_description": "[마스터 레벨 : 1]\r\n달빛의 힘으로 자신의 공격력과 마력을 7씩 증가시킨다.",
                "skill_level": 1,
                "skill_effect": "공격력 7, 마력 7증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHOEJA.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(attack_power=7, magic_attack=7)),
        ),
        (
            {
                "skill_name": "루나 드림 Lv.1",
                "skill_description": "[마스터 레벨 : 1]\r\n달빛의 힘으로 자신의 공격력과 마력을 7씩 증가시킨다.",
                "skill_level": 1,
                "skill_effect": "공격력 7, 마력 7증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHOEKD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(attack_power=7, magic_attack=7)),
        ),
        (
            {
                "skill_name": "째깍째깍 동화 시간 Lv.1",
                "skill_description": "[마스터 레벨 : 1]\r\n쁘띠 마스터 타임 펫의 동화 속 마법같은 힘으로 자신의 공격력과 마력을 8씩 증가시킨다.",
                "skill_level": 1,
                "skill_effect": "공격력 8, 마력 8증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHOGLD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(attack_power=8, magic_attack=8)),
        ),
        (
            {
                "skill_name": "리스트레인트 링",
                "skill_description": "[마스터 레벨 : 5]\r\n일정 시간 동안 생성되는 영역 안에서 자신의 공격력과 마력을 증가시킨다. 영역을 벗어나면 영역이 소멸한다.\n재사용 대기시간 초기화의 효과를 받지 않는다.",
                "skill_level": 4,
                "skill_effect": "HP 600 소비, 15초 동안 생성되는 영역 안에서 자신의 공격력이 100%, 마력이 100% 증가\n재사용 대기시간 180초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHPFJF.png",
                "skill_effect_next": "HP 600 소비, 20초 동안 생성되는 영역 안에서 자신의 공격력이 100%, 마력이 100% 증가\n재사용 대기시간 180초",
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "여왕님이 함께 하셔!",
                "skill_description": "[마스터 레벨 : 2]\r\n블러디퀸의 마음은 갈대와 같아서 그때그때 기분에 따라 다른 모습으로 나타난다. \n소울스킬 사용 시 유혹의 블러디퀸, 기쁨의 블러디퀸, 분노의 블러디퀸, 슬픔의 블러디퀸 중 하나의 블러디퀸이 등장합니다.",
                "skill_level": 1,
                "skill_effect": "250 소울을 소비하여 90초 동안 데미지 1500%의 블러디퀸 소환\n소울웨폰 소환수의 데미지는 캐릭터와 다르게 계산됨\n재사용 대기시간 150초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHPGMA.png",
                "skill_effect_next": "250 소울을 소비하여 90초 동안 데미지 1800%의 블러디퀸 소환\n소울웨폰 소환수의 데미지는 캐릭터와 다르게 계산됨\n재사용 대기시간 150초",
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "메이플 휘장",
                "skill_description": "[마스터 레벨 : 1]\r\n메이플 업적에서 선택한 휘장을 실체화한다.\n실체화된 휘장은 일정 시간 동안 캐릭터 주위에 머무르다가 사라진다. 업적 등급 및 완료 업적에 따라 다양한 휘장을 선택하여 실체화시킬 수 있다.",
                "skill_level": 1,
                "skill_effect": "재사용 대기시간 5초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHMCOD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "파괴의 얄다바오트",
                "skill_description": "[마스터 레벨 : 1]\r\n검은 마법사가 초월자의 힘으로 만들어 낸 파괴의 얄다바오트가 깃들어 힘을 발휘한다.\n스킬 사용 시 효과가 활성화되고 재사용 시 비활성화되는 온오프 스킬",
                "skill_level": 1,
                "skill_effect": "영구적으로 최종 데미지 10% 증가\n스킬 사용 시 파괴의 얄다바오트 소환",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHMHPC.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat(final_damage_multiplier=10)),
        ),
        (
            {
                "skill_name": "창조의 아이온",
                "skill_description": "[마스터 레벨 : 1]\r\n검은 마법사가 초월자의 힘으로 만들어 낸 창조의 아이온을 소환하여 그 힘을 이용한다.\n재사용 대기시간 초기화 및 버프 지속시간 증가의 효과를 받지 않고 창세의 기운은 공격 반사 상태의 적을 공격해도 피해를 입지 않는다.",
                "skill_level": 1,
                "skill_effect": "창조의 힘을 발현하여 10초 동안 무적 상태\n스킬을 다시 사용하여 즉시 종료 가능, 즉시 종료하면 12명의 적을 1500%의 데미지로 7번 공격하는 창세의 기운 발동\n재사용 대기시간 120초",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHMHPD.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "링 액티베이션",
                "skill_description": "[마스터 레벨 : 1]\n현재 착용 중인 특수 스킬 반지의 액티브 스킬을 사용한다.\n일부 특수 스킬 반지의 경우 패시브 스킬이 자동으로 발동된다.",
                "skill_level": 1,
                "skill_effect": "사용 시 현재 장착한 특수 스킬 반지의 액티브 스킬 발동",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHNBPE.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
        (
            {
                "skill_name": "고브의 선물",
                "skill_description": "[마스터 레벨 : 1]\r\n신비한 힘이 깃든 고대신 고브의 특별한 선물이다.",
                "skill_level": 1,
                "skill_effect": "공격력/마력 10 증가\r\n보스 몬스터 공격 시 데미지 35% 증가\r\n몬스터 방어율 무시 35% 증가\r\n올스탯 10 증가\r\n버프 지속시간 15% 증가\r\n일반 몬스터 공격 시 데미지 10% 증가\r\n폴로/프리토/에스페시아, 불꽃늑대 획득 경험치 80% 증가\r\n몬스터파크 퇴장 시 획득하는 경험치 40% 증가",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHNGKG.png",
                "skill_effect_next": None,
            },
            ExtendedStat(
                stat=Stat(
                    attack_power=10,
                    magic_attack=10,
                    boss_damage_multiplier=35,
                    ignored_defence=35,
                    STR=10,
                    DEX=10,
                    INT=10,
                    LUK=10,
                ),
                action_stat=ActionStat(buff_duration=15),
            ),
        ),
        (
            {
                "skill_name": "챔피언 더블 업",
                "skill_description": "챔피언으로 지정된 캐릭터들이 챔피언 리더를 따라다닌다.\n\n우클릭으로 ON/OFF 할 수 있다.",
                "skill_level": 1,
                "skill_effect": "챔피언들이 함께 다니는 모습을 볼 수 있다.\nOFF 시, 따라다니는 모습만 보이지 않게 된다.",
                "skill_icon": "https://open.api.nexon.com/static/maplestory/SkillIcon/KFHCLHNGLA.png",
                "skill_effect_next": None,
            },
            ExtendedStat(stat=Stat()),
        ),
    ],
)
def test_zero_grade_skill_effect(skill_effect, expected):
    assert _get_passive_skill_effect_from_description(skill_effect) == expected
