# Comments or Issues? Guidelines to Report Technical Debt

_Self-Admitted Technical Debt (SATD) is a particular case of Technical Debt (TD) in which developers rely on source code comments (SATD-C) or labeled issues (SATD-I) to report their sub-optimal technical solutions. However, it is still unclear the interplay that exists between these two strategies to document TD, and the circumstances that drive developers to choose one or another. In this paper, we first build a large dataset of 74K SATD-C and 20K SATD-I instances, extracted from 190 well-known GitHub projects. We also implement a prototype tool, called AdmiTD, to automatically report SATD-C as GitHub issues. We use this dataset and tool to reveal that there is a minor interplay between SATD-C and SATD-I. For example, less than 1% of SATD-C instances in our dataset include a reference to SATD-I instances. We also concluded that developers are not interested in the automatic transformation of SATD-C in SATD-I, even after implementing some basic filtering heuristics in our prototype tool. Finally, we elicited a catalog of 11 guidelines to support developers to decide whether to use comments or issues to report TD._

## Authors

Ommited due to DBR

## Instructions

Please, find:

* AdmiTD source code at /admitd
* Datasets at /dataset
* Python and R scripts at /scripts 
