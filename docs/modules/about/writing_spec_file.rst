*****************************
About: Spec
*****************************

.. contents:: Contents
    :local:


이 문서에서는 simaple에서 데이터를 다룰 때 사용하는 Spec을 작성하는 방법에 대해 기술합니다.
이 문서는 라이브러리 코드를 해석하고자하는 개발자에게 필요합니다; 라이브러리 사용자가 Spec에 대해 이해할 필요는 없습니다.


Introduction
======================

simaple은 사용자의 편의를 위해, 게임 내에 존재하는 값들을 명시한, 데이터 다수를 제공합니다. 
이러한 데이터에는 직업군간 비교를 위한 아이템 세팅인 Baseline, 각 스킬의 스킬 정보를 기술하는 Component, 농장별 스펙, 도핑 등이 포함됩니다.
데이터를 코드로부터 분리함으로서, simaple의 라이브러리는 효과적으로 구현을 추상화로부터 분리합니다.

simaple 라이브러리 내의 모든 빌트인 데이터는 Spec이라는 yaml file을 통해 표현됩니다.
여러분이 라이브러리에 기여하고자 한다면, 빌트인 데이터를 이해하고 작성하기 위해 이에 대해 알 필요가 있습니다.


Definition
===============

Spec은 python class로 즉시 변환 가능한 yaml file입니다. 간단한 예시를 살펴봅시다.

.. code-block:: yaml

    kind: NamedStat 
    version: simaple.io/Doping
    metadata:
      label:
        name: 전설의 영웅 비약
        level: normal
    data:  
      name: 전설의 영웅 비약
      stat: 
        attack_power: 30
        magic_attack: 30


Spec의 동작 방식을 이해하기 위해, 해당 Spec이 해석될 때 사용될 클래스를 함께 봅시다.

.. code-block:: python

    import pydantic

    from simaple.core import ActionStat, ExtendedStat, Stat
    from simaple.spec.loadable import (  # pylint:disable=unused-import
        TaggedNamespacedABCMeta,
    )


    class NamedStat(
        pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="NamedStat")
    ):
        name: str
        stat: Stat = pydantic.Field(default_factory=Stat)
        action_stat: ActionStat = pydantic.Field(default_factory=ActionStat)

        def get_extended_stat(self) -> ExtendedStat:
            return ExtendedStat(
                stat=self.stat.copy(),
                action_stat=self.action_stat.copy(),
            )

        def get_name(self) -> str:
            return self.name

    class Doping(NamedStat):
        ...


Spec은 k8s manifest를 참고하여 만들어졌으며, 따라서 각 필드의 역할 또한 유사합니다.

- ``kind`` 는 생성될 수 있는 class의 부모 클래스를 명시합니다.
  부모 클래스는 ``TaggedNamespacedABCMeta`` 를 통해 정의된 metaclass로부터 생성됩니다. 
  ``kind=NamedStat`` 로 지정되었기 때문에, NamedStat class 를 부모로 갖는 모든 클래스는 ``kind=NamedStat`` 명세가 있는 Spec을 통해 생성될 수 있습니다.

- ``version`` 은 생성될 class의 이름을 명시합니다. class의 이름은 버저닝의 / 다음 값을 통해 결정됩니다.
  ``simaple.io/Doping`` 에서, 우리는 이 Spec이 ``Doping`` class 인스턴스를 생성할 것임을 알 수 있습니다.
  prefix인 ``simaple.io`` 는 현재로는 사용되지 않습니다.

- ``metadata`` 는 해당 데이터가 가지고 있기를 바라는 메타데이터 정보를 기입합니다. ``metadata`` 는 다시 두 가지로 나뉩니다.
  - ``label`` 은 이 데이터를 탐색을 통해 찾고자 할 때 사용되기를 바라는 값들의 집합입니다.
  - ``annotation`` 은 탐색에 사용될 값은 아니지만, 데이터를 참고하려는 사람이 알고있기를 바라는 값들의 집합입니다.
  
  우리는 해당 데이터가 ``name=전설의 영웅 비약`` 과 같이 조회했을 때 포착되기를 원하므로, label에 기입합니다.

- ``data`` 는 클래스를 생성하기 위해 사용될 값입니다. 모든 ``Spec`` 으로 작성되는 클래스는 ``pydantic.BaseModel`` 을 상속합니다. 여기에 작성되는 값은, 해당 클래스를 ``parse_raw`` 함수를 호출하여 생성하고자 할 때 입력될 값입니다.
  ``Doping`` 은 ``stat`` 필드에 ``Stat`` 객체를 요구하므로, 위와 같이 기입하면 충분합니다.
  이를 통해 생성될 객체는 아래와 동등할 것입니다.

  .. code-block:: python
     
     doping = Doping.parse_raw({"stat": {"attack_power": 30, "magic_attack": 30})


Interpreting Spec into class object
======================================

작성한 Spec file을 대응되는 클래스 인스턴스로 변경하기 위해서는 Spec class로 생성한 뒤 해석하면 충분합니다.

.. code-block:: python

    from simaple.spec.spec import Spec
    import yaml


    spec = Spec.parse_obj(yaml.safe_load(open("file-name")))
    cls_obj = spec.interpret()


Using Loader
==============

Spec은 데이터이므로, 직접 파일을 통해 파일의 경로를 참조하는 loader를 통해 불러와야 합니다.
loader는 해당 경로 내에 존재하는 모든 spec을 저장하고, 불러올 수 있도록 돕습니다.

.. code-block:: python

    from simaple.spec.loader import SpecBasedLoader
    from simaple.spec.repository import DirectorySpecRepository

    repository = DirectorySpecRepository("yaml-files-dir/")
    loader = SpecBasedLoader(repository)
    loaded_specs = loader.load_all(
        query={"group": jobtype.value, "kind": "PassiveSkill"},
    )

query에 기입된 정보는 ``metadata.label`` 에 일치하는 값을 가져오게 됩니다.


Patch
==========

Spec은 simaple에 정의된 객체의 parse_raw 생성 함수를 호출하는 것과 동등합니다. 
하지만, 라이브러리 상의 모든 class는 데이터 주입을 고려하지 않고 설계되기 때문에, 데이터의 관점에서는 친절하지 않은 경우가 많습니다.
이러한, 데이터와 도메인 관점에서의 인터페이스 요구사항 불일치를 해소하기 위해 Spec은 Patch를 지원합니다.
Patch는 data field에 작성된 dictionary를 입력으로 받아 그 값을 변조합니다.

Patch는 patch field에 적용되어야 하는 Patch들을 기입하고, 내부 데이터를 변형함으로서 사용됩니다.
Patch의 용법을 Spec을 보면서 확인해봅시다. 아래는 PassiveSkill Spec입니다.

.. code-block:: yaml

    kind: PassiveSkill
    version: simaple.io/PassiveSkill
    metadata:
      label:
        group: archmagefb
    patch:
    - SkillLevelPatch
    - EvalPatch
    data:
      name: 아케인 에임
      passive_skill_enabled: true
      default_skill_level: 30
      stat:
        ignored_defence: "{{ 5 + math.ceil(skill_level / 2) }}"


위 Spec에는 두 가지 Patch, SkillLevelPatch와 EvalPatch가 적용되어야 한다고 명시되어 있습니다.
따라서 PassiveSkill을 위 yaml로부터 생성하기 위해서는 interpret할 때 아래와 같이 patch를 넘겨주어야 합니다.

.. code-block:: python


    from simaple.spec.spec import Spec
    import yaml

    spec = Spec.parse_obj(yaml.safe_load(open("file-name")))
    cls_obj = spec.interpret(
        patches=[
            SkillLevelPatch(
                combat_orders_level=1,
                passive_skill_level=0,
            ),
            EvalPatch(
                injected_values={
                    "character_level": 260,
                    "weapon_pure_attack_power": 987,
                }
            )
        ],
    })

제시된 데이터가 Patch가 적용됨에 따라 아래와 같이 변조됩니다. Patch는 앞에 있는 것부터 적용됩니다.

.. code-block:: python 

    # Initial
    {
        "name": "아케인 에임",
        "passive_skill_enabled": True,
        "default_skill_level": 30,
        "stat":{
            "ignored_defence": "{{ 5 + math.ceil(skill_level / 2) }}"
        }
    }

    # After SkillLevelPatch

    {
        "name": "아케인 에임",
        "passive_skill_enabled": True,
        "default_skill_level": 30,
        "stat":{
            "ignored_defence": "{{ 5 + math.ceil( 31 / 2) }}"
        }
    }

    # After SkillLevelPatch, EvalPatch

    {
        "name": "아케인 에임",
        "passive_skill_enabled": True,
        "default_skill_level": 30,
        "stat":{
            "ignored_defence": 21
        }
    }


데이터의 변경 과정에서 보다시피, Patch는 제공된 데이터 전체를 참조하여 변경함으로서, 제시된 데이터가 해당 class (여기서는 PassiveSkill) 에 알맞은 포맷이 되도록 변경합니다.

이러한 과정이 필요한것은, 우리가 묘사하고자 하는 데이터와 클래스의 구현간 괴리 때문입니다. 
PassiveSkill은 스킬 레벨에 대한 구현을 하고있지 않습니다. 
따라서, Patch가 없다면, 우리는 스킬 레벨별로 Spec을 작성하고, 레벨마다 label을 하여야 했을 것입니다.
Patch는 데이터 도메인에 필요한 기능을 구현함으로서, 우리가 작성한 yaml이 실제 class의 입력값과 다르게 추상화되더라도, 여전히 올바르게 해석될 수 있도록 여지를 제공합니다.

물론, Spec에 Patch가 적용되면, 그 Spec에는 Patch를 적용하지 않고서는 해석이 불가능합니다. 
따라서, patch field에 명시된 Patch가 모두 제공되지 않으면 Spec은 해석되지 않습니다.

