**************************
Examples
**************************

.. contents:: Contents
    :local:


Benchmark Example
=================

Benchmark는 제시된 직업에 알맞은, 설정된 장비 수준의 ``Geatset`` 을 불러옵니다.


아래와 같은 Builtin Benchmark를 지원합니다.

- Epic
- EpicUnique
- Unique
- LegendaryHalf
- Legendary18
- Legendary


Create Gearset From Baseline
-----------------------------

::

    from simaple.data.baseline import get_baseline_gearset
    from simaple.core import JobCategory
    from simaple.gear.gear_repository import GearRepository

    gearset = get_baseline_gearset("EpicUnique", JobCategory.warrior)
    print(gearset.get_total_extended_stat().stat.show())


Fetch Example
=============

Hompage data fetch 
-------------------

::

    from simaple.fetch.application.base import KMSFetchApplication
    from simaple.gear.slot_name import SlotName

    app = KMSFetchApplication()

    character_response = app.run("Character-Name")



Infer Character Spec 
--------------------

::

    from simaple.fetch.application.base import KMSFetchApplication
    from simaple.gear.slot_name import SlotName
    from simaple.fetch.inference.builtin_settings import infer_stat_by_default

    app = KMSFetchApplication()

    character_response = app.run("Character-Name")
    result = infer_stat_by_default(character_response, authentic_force=390, size=5)
    assert len(result) == 
    print(result[0].short_dict())


Load Item information
---------------------

::

    from simaple.fetch.application.base import KMSFetchApplication
    from simaple.gear.slot_name import SlotName

    app = KMSFetchApplication()

    character_response = app.run("Character-Name")
    cap = character_response.get_item(SlotName.cap)

    print(cap.show())


Load raw-data for custom application
------------------------------------------

::

    from simaple.fetch.application.base import KMSFetchApplication

    character_response = app.run("Character-Name")
    raw_data = character_response.get_raw()

    print(raw_data)

