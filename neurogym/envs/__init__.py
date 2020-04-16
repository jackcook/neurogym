import importlib
from inspect import getmembers, isfunction

import gym
from gym.envs.registration import register


ALL_NATIVE_ENVS = {
    'ContextDecisionMaking-v0':
        'neurogym.envs.contextdecisionmaking:ContextDecisionMaking',
    'DelayedComparison-v0':
        'neurogym.envs.delayedcomparison:DelayedComparison',
    'PerceptualDecisionMaking-v0':
        'neurogym.envs.perceptualdecisionmaking:PerceptualDecisionMaking',
    'EconomicDecisionMaking-v0':
        'neurogym.envs.economicdecisionmaking:EconomicDecisionMaking',
    'PostDecisionWager-v0':
        'neurogym.envs.postdecisionwager:PostDecisionWager',
    'DelayPairedAssociation-v0':
        'neurogym.envs.delaypairedassociation:DelayPairedAssociation',
    'GoNogo-v0':
        'neurogym.envs.gonogo:GoNogo',
    'ReadySetGo-v0':
        'neurogym.envs.readysetgo:ReadySetGo',
    'OneTwoThreeGo-v0':
        'neurogym.envs.readysetgo:OneTwoThreeGo',
    'DelayedMatchSample-v0':
        'neurogym.envs.delaymatchsample:DelayedMatchToSample',
    'DelayedMatchCategory-v0':
        'neurogym.envs.delaymatchcategory:DelayedMatchCategory',
    'DawTwoStep-v0':
        'neurogym.envs.dawtwostep:DawTwoStep',
    'HierarchicalReasoning-v0':
        'neurogym.envs.hierarchicalreasoning:HierarchicalReasoning',
    'MatchingPenny-v0':
        'neurogym.envs.matchingpenny:MatchingPenny',
    'MotorTiming-v0':
        'neurogym.envs.readysetgo:MotorTiming',
    'MultiSensoryIntegration-v0':
        'neurogym.envs.multisensory:MultiSensoryIntegration',
    'Bandit-v0':
        'neurogym.envs.bandit:Bandit',
    'PerceptualDecisionMakingDelayResponse-v0':
        'neurogym.envs.perceptualdecisionmaking:PerceptualDecisionMakingDelayResponse',
    'NAltPerceptualDecisionMaking-v0':
        'neurogym.envs.nalt_perceptualdecisionmaking:nalt_PerceptualDecisionMaking',
    # 'Combine-v0': 'neurogym.envs.combine:combine',
    # 'IBL-v0': 'neurogym.envs.ibl:IBL',
    # 'MemoryRecall-v0': 'neurogym.envs.memoryrecall:MemoryRecall',
    'Reaching1D-v0':
        'neurogym.envs.reaching:Reaching1D',
    'Reaching1DWithSelfDistraction-v0':
        'neurogym.envs.reaching:Reaching1DWithSelfDistraction',
    'AntiReach-v0':
        'neurogym.envs.antireach:AntiReach1D',
    'DelayedMatchToSampleDistractor1D-v0':
        'neurogym.envs.delaymatchsample:DelayedMatchToSampleDistractor1D',
    'IntervalDiscrimination-v0':
        'neurogym.envs.intervaldiscrimination:IntervalDiscrimination',
    'AngleReproduction-v0':
        'neurogym.envs.anglereproduction:AngleReproduction',
    'Detection-v0':
        'neurogym.envs.detection:Detection',
    'ReachingDelayResponse-v0':
        'neurogym.envs.reachingdelayresponse:ReachingDelayResponse',
    'CVLearning-v0':
        'neurogym.envs.cv_learning:CVLearning',
    'ChangingEnvironment-v0':
        'neurogym.envs.changingenvironment:ChangingEnvironment',
    'ProbabilisticReasoning-v0':
        'neurogym.envs.weatherprediction:ProbabilisticReasoning',
    'DualDelayedMatchSample-v0':
        'neurogym.envs.dualdelaymatchsample:DualDelayedMatchToSample',
    'PulseDecisionMaking-v0':
        'neurogym.envs.perceptualdecisionmaking:PulseDecisionMaking',
    'Nothing-v0':
        'neurogym.envs.nothing:Nothing'
}

ALL_PSYCHOPY_ENVS = {
    'psychopy.RandomDotMotion-v0':
        'neurogym.envs.psychopy.perceptualdecisionmaking:RandomDotMotion',
    'psychopy.VisualSearch-v0':
        'neurogym.envs.psychopy.visualsearch:VisualSearch',
}


# Automatically register all tasks in collections
def _get_collection_envs():
    # TODO: keep making this more general
    derived_envs = {}
    collection_libs = ['cogneuro', 'yang19']
    for l in collection_libs:
        lib = 'neurogym.envs.collections.' + l
        module = importlib.import_module(lib)
        envs = [name for name, val in getmembers(module) if isfunction(val)]
        envs = [env for env in envs if env[0] != '_']  # ignore private members
        derived_envs.update({env+'-v0': lib + ':' + env for env in envs})
    return derived_envs


ALL_COLLECTIONS_ENVS = _get_collection_envs()

ALL_ENVS = {
    **ALL_NATIVE_ENVS, **ALL_PSYCHOPY_ENVS
}

ALL_EXTENDED_ENVS = {**ALL_ENVS, **ALL_COLLECTIONS_ENVS}


def all_envs(tag=None):
    """Return a list of all envs in neurogym."""
    env_list = sorted(list(ALL_ENVS.keys()))
    if tag is None:
        return env_list
    else:
        if not isinstance(tag, str):
            raise ValueError('tag must be str, but got ', type(tag))

        new_env_list = list()
        for env in env_list:
            from_, class_ = ALL_ENVS[env].split(':')
            imported = getattr(__import__(from_, fromlist=[class_]), class_)
            env_tag = imported.metadata.get('tags', [])
            if tag in env_tag:
                new_env_list.append(env)
        return new_env_list


_all_gym_envs = [env.id for env in gym.envs.registry.all()]
for env_id, entry_point in ALL_EXTENDED_ENVS.items():
    if env_id not in _all_gym_envs:
        register(id=env_id, entry_point=entry_point)


def all_tags():
    return ['confidence', 'context dependent', 'continuous action space', 'delayed response', 'go-no-go',
            'motor', 'multidimensional action space', 'n-alternative', 'perceptual', 'reaction time',
            'steps action space', 'supervised', 'timing', 'two-alternative', 'value-based', 'working memory']


__all__ = ['multisensory']