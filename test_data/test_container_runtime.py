import os

from inline_snapshot import snapshot

import simaple.simulate.component.common  # pylint: disable=W0611
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import get_damage_calculator, get_operation_engine
from simaple.core.jobtype import JobType
from simaple.data.jobs.builtin import get_builtin_strategy
from simaple.simulate.report.base import SimulationEntry
from simaple.simulate.strategy.base import exec_by_strategy


def container_test_setting(
    jobtype,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=jobtype,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        weapon_attack_power=options.get("weapon_attack_power", 0),
    )


def run_actor(environment_provider: BaselineEnvironmentProvider, jobtype: JobType):
    environment = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".memo.simaple.json")
    ).compute_environment(environment_provider)
    engine = get_operation_engine(environment)

    policy = get_builtin_strategy(environment.jobtype).get_priority_based_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        exec_by_strategy(engine, policy)

    report = list(engine.simulation_entries())

    """
    with open("operation.log", "w") as f:
        for op in engine.operation_logs():
            f.write(op.operation.expr+'\n')

    with open("history.log", "w") as f:
        for op in engine.operation_logs():
            for playlog in op.playlogs:
                f.write(f"{playlog.clock} | {playlog.action} | {playlog.events} \n")
    """

    damage_calculator = get_damage_calculator(environment)

    def aggregate_by_skill(report: list[SimulationEntry]):
        skill_dpm = {}
        for entry in report:
            for log in entry.damage_logs:
                if log.name not in skill_dpm:
                    skill_dpm[log.name] = 0
                skill_dpm[log.name] += damage_calculator.get_damage(log)
        return skill_dpm

    result = aggregate_by_skill(report)
    dpm = damage_calculator.calculate_dpm(report)
    print(f"{engine.get_current_viewer()('clock')} | {jobtype} | {dpm:,} ")
    print(result)
    return result, dpm


def test_archmagefb_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagefb)

    # when
    result, dpm = run_actor(environment_provider, JobType.archmagefb)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "이프리트": 166201268673.88593,
                "인페르날 베놈": 4541530492596.879,
                "파이어 오라": 275612879308.63904,
                "메테오(패시브)": 573926302670.3467,
                "이그나이트": 804646740476.5568,
                "메테오": 87770381760.6306,
                "포이즌 노바": 670895441868.0095,
                "도트 퍼니셔": 960432544080.6763,
                "메기도 플레임": 239239348679.7172,
                "퓨리 오브 이프리트": 838933573917.09,
                "미스트 이럽션 VI": 1564791138165.2288,
                "포이즌 체인": 567098229993.8036,
                "플레임 헤이즈 VI": 639707460982.4912,
                "포이즌 미스트": 91785758911.9797,
                "플레임 스윕 VI": 1556951032516.4187,
            },
            16156481373708.904,
        )
    )


def test_archmagetc_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagetc)

    # when
    result, dpm = run_actor(environment_provider, JobType.archmagetc)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "프로즌 라이트닝": 1500539404930.1528,
                "엘퀴네스": 102170406751.72746,
                "프로즌 라이트닝 (마력 개화)": 755407134044.1227,
                "아이스 에이지": 100452155384.77737,
                "라이트닝 스피어": 767742698994.1427,
                "아이스 에이지 (지면)": 273400164877.8858,
                "스피릿 오브 스노우": 1419002248859.9558,
                "블리자드 VI": 68008664499.68281,
                "주피터 썬더": 1423461930682.9995,
                "썬더 브레이크": 848924787448.6373,
                "프로즌 오브 VI": 563789477917.4707,
                "블리자드 VI(패시브)": 483629763209.81323,
                "체인 라이트닝 VI": 2536372338153.0586,
            },
            12900536794472.836,
        )
    )


def test_bishop_actor():
    # given
    environment_provider = container_test_setting(JobType.bishop)

    # when
    result, dpm = run_actor(environment_provider, JobType.bishop)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "엔젤릭 터치": 8953248660.488129,
                "제네시스": 97154174570.16805,
                "트라이엄프 페더 VI": 937029959081.3287,
                "바하뮤트": 373767382415.8405,
                "헤븐즈 도어": 74883465963.12552,
                "파운틴 포 엔젤": 317345414867.4437,
                "피스메이커": 532928109469.03735,
                "디바인 퍼니시먼트": 1656212961973.5037,
                "엔젤 오브 리브라": 856642007298.3612,
                "엔젤레이 VI": 2972530818262.5854,
            },
            9374188673726.805,
        )
    )


def test_mechanic_actor():
    # given
    environment_provider = container_test_setting(JobType.mechanic)

    # when
    result, dpm = run_actor(environment_provider, JobType.mechanic)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "메카 캐리어": 2323690801869.781,
                "로봇 런처: RM7": 101741584493.53297,
                "마그네틱 필드": 118967418055.26521,
                "로봇 팩토리: RM1": 289578962787.2895,
                "멀티플 옵션: M-FL": 743458014782.7113,
                "메탈아머 전탄발사": 1569310757896.2986,
                "마이크로 미사일 컨테이너": 1205315466811.9077,
                "디스토션 필드": 262772716670.4316,
                "레지스탕스 라인 인팬트리": 193629931601.2143,
            },
            7978670689416.144,
        )
    )


def test_adele_actor():
    # given
    environment_provider = container_test_setting(
        JobType.adele,
        {
            "weapon_attack_power": 700,
            "weapon_pure_attack_power": 295,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.adele)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "인피니트": 3387406381980.7188,
                "마커": 159288611961.12234,
                "그레이브": 102023930586.62256,
                "테리토리": 658450795349.8411,
                "리스토어": 250678438952.07968,
                "루인": 473405530806.8826,
                "레조넌스": 2529598801823.5903,
            },
            9022497006516.545,
        )
    )


def test_windbreaker_actor():
    # given
    environment_provider = container_test_setting(
        JobType.windbreaker,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.windbreaker)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "가이디드 애로우": 289263002417.52545,
                "핀포인트 피어스": 6518457077.807544,
                "스톰 브링어": 648514698983.4133,
                "스톰 윔": 600478042953.0562,
                "윈드 월": 1172933192182.8538,
                "하울링 게일": 3234952605978.3325,
                "볼텍스 스피어": 853721121595.9148,
                "시그너스 팔랑크스": 467406313222.39417,
                "아이들 윔": 666392330801.41,
                "천공의 노래 VI": 1335690545905.994,
            },
            11108826719902.613,
        )
    )


def test_soulmaster_actor():
    # given
    environment_provider = container_test_setting(
        JobType.soulmaster,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.soulmaster)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "코스모스": 1058646627520.156,
                "소울 이클립스": 1784959367581.5486,
                "크로스 더 스틱스": 4823730903074.457,
                "코스믹 버스트": 900609423810.4683,
                "플레어 슬래시": 289591670403.53485,
                "코스믹 샤워": 349553191210.878,
                "엘리시온": 603336387488.8949,
                "솔라 슬래시/루나 디바이드": 751814637264.92,
            },
            12626709155235.973,
        )
    )


def test_dualblade_actor():
    # given
    environment_provider = container_test_setting(
        JobType.dualblade,
        {
            "weapon_attack_power": 700,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.dualblade)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "플래시 뱅": 1424870847.5598774,
                "히든 블레이드": 410811177939.6261,
                "파이널 컷": 3611272252.2719283,
                "써든레이드": 50072324297.917366,
                "블레이드 토네이도": 185701214833.68533,
                "블레이드 토네이도 (태풍)": 397053416618.3776,
                "카르마 퓨리": 671382774764.1117,
                "아수라 VI": 595366309890.1576,
                "블레이드 스톰": 1158430837805.2253,
                "팬텀 블로우 VI": 1596134682129.8054,
                "헌티드 엣지 - 나찰": 312666081743.23944,
            },
            6439866356676.321,
        )
    )
