<!-- INSTRUCTIONS: 
- READ/FOLLOW THE DIRECTIONS IN EACH SECTION
- Complete the 'Commit Requirements' below
- Use GitHub markup as much as possible (https://docs.github.com/en/get-started/writing-on-github)
- Leave your PR in a draft state until all underlying work is completed.
-->

## Description:
<!-- This description will become the commit message for the PR. -->
<!-- See https://cbea.ms/git-commit for commit message suggestions. -->
<!--
Provide a clear and concise description of *what* this PR does and *why*.
Explain why this change is needed and any context that helps reviewers.
Add the related GitHub Issues here.
Please be sure to add the issue this PR resolves using the word "Resolves". If there are any issues that are related but not yet resolved (including in other repos), you may use "Refs".
Resolves #1234
Refs #4321
Refs NOAA-EPIC/repo#5678
-->

## Type of change:
<!--
Indicate PR type of change.
Delete options that are not applicable. 
-->
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor / cleanup
- [ ] Documentation
- [ ] CI/CD or tooling
- [ ] Other:

## Area(s) affected
<!-- Check all that apply -->
- [ ] nested_eagle workflow
- [ ] Verification / evaluation (via WXVX)
- [ ] Data prep / UFS2ARCO
- [ ] Config (YAML)
- [ ] Plotting / post-processing
- [ ] Infrastructure / Slurm scripts
- [ ] Other:

## Commit Requirements:
<!--
- Check off completed items. Use [X] for a filled in checkbox or leave it [ ] for an empty checkbox
- Your pull request (PR) will not be considered until all requirements are met.
- THIS IS YOUR RESPONSIBILITY
-->
- [ ] This PR addresses a relevant NOAA-EPIC/EAGLE issue (if not, create an issue); a person responsible for submitting the update has been assigned to the issue (link issue)
- [ ] Fill out all sections of this template.
- [ ] I have performed a self-review of my own code
- [ ] My changes generate no new warnings
- [ ] I have made corresponding changes to the system documentation if necessary

## Testing / Verification:
<!--
Provide minimal reproducible steps and results.
Include configs, commands, and expected outputs where possible.
Delete this section if not applicable.
-->
- [ ] I ran and/or verified the changes (or provided a test plan)
- Commands/config used:
  - 
- Evidence (logs, key output paths, screenshots if relevant):
  - 

## Runtime Environment:
<!--
Fill in if you ran on HPC or a specific system. Delete if not applicable.
-->
- System/HPC:
- Account/role:
- Conda env:
- Key versions (optional):
  - `python --version`:
  - `wxvx --version` (if applicable):
  - MET version (if applicable):

## Commit Message:
<!--
Provide a concise commit message for any subcomponents; delete unnecessary info.
-->
* UFS2ARCO -
* WXVX (verification) -

## Subcomponent Pull Requests:
<!--
Provide a list of NOAA-EPIC/EAGLE and subcomponents involved with this PR and include links to subcomponent PRs.
Example:
* EAGLE: NOAA-EPIC/EAGLE#13
* UFS2ARCO: NOAA-PSL/UFS2ARCO#734
* WXVX: NOAA-EPIC/WXVX#33
Delete sections that are not needed.
-->
* EAGLE: NOAA-EPIC/EAGLE#
* UFS2ARCO: NOAA-PSL/UFS2ARCO#
* WXVX (verification): NOAA-EPIC/WXVX#
* None

