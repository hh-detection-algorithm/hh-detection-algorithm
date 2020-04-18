from algorithms.hashpipe.hashpipe import HashPipe
from algorithms.hashpipe.hashpage import HashPage
from algorithms.hashpipe.hashslide import HashSlide

from algorithms.cms.cms import CMS
from algorithms.cms.cms_slide import CMSSlide
from algorithms.cms.cms_page import CMSPAge

from algorithms.ss.ss import SpaceSaving
from algorithms.ss.ss_slide import SpaceSavingSlide
from algorithms.ss.ss_page import SpaceSavingPAge


def get_algorithm(args):
    algorithm = args.algorithm
    sliding_window = args.sliding_window
    aging_factor = args.aging_factor

    assert(sliding_window ^ aging_factor == 1 or sliding_window | aging_factor == 0)

    if algorithm == 'ss':
        if sliding_window:
            return SpaceSavingSlide(args)
        elif aging_factor:
            return SpaceSavingPAge(args)
        else:
            return SpaceSaving(args)
    elif algorithm == 'hashpipe':
        if sliding_window:
            return HashSlide(args)
        elif aging_factor:
            return HashPage(args)
        else:
            return HashPipe(args)
    elif algorithm == 'cms':
        if sliding_window:
            return CMSSlide(args)
        elif aging_factor:
            return CMSPAge(args)
        else:
            return CMS(args)
