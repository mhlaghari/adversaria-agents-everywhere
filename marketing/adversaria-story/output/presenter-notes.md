# Why I built Adversaria

## Slide 1

I am Hamza, a lead AI engineer. Adversaria is an ongoing project I am building at Laghari Labs. I built it because my meetings kept producing more work while my own projects waited. Today I extended the desktop Copilot and Spaces experience and built a terminal edition.

## Slide 2

As a lead AI engineer, I attend many meetings. In my experience, an action item can take another hour or two. The work might be researching an approach or turning the discussion into a solution architecture. The meeting ends, but that work remains. The time estimate is my experience, not a claim about everyone or a measured time saving.

## Slide 3

I still have my own projects to build. When every meeting produces more follow-up, those projects get whatever time is left. That is the personal pain behind Adversaria. I wanted the context and commitments from a meeting to help me start the actual work.

## Slide 4

Adversaria starts with a local desktop meeting workflow. It captures the meeting and keeps transcripts and notes locally. In local mode, the desktop can use on-device transcription and AI. It also supports optional external providers. Workspace web research and cloud agents require external services, so I do not describe those paths as completely local. The local notes workflow is the foundation.

## Slide 5

During a meeting, Copilot uses the discussion to suggest useful context and talking points. It also catches commitments and presents the follow-up for my review. That means I can stay in the conversation and still see what needs to happen afterward.

## Slide 6

Spaces, called Workspaces in the app, connect meeting context to work. I can approve an action item, research options and create a solution architecture diagram inside the workspace. Then I review the artifact. The diagram and research are drafts for engineering judgment. Web research uses external services when enabled. Human review remains part of the workflow.

## Slide 7

Today I built on the existing Copilot and Spaces foundation, including a compact companion and inline diagram preview. I also built Adversaria CLI: a terminal meeting copilot and work interface. It uses configured provider credentials. OpenRouter handles cloud speech and models, Exa handles web research, and OpenAI is an optional direct model and transcription provider. Codex task execution uses a separate Codex login, not a provider API key. This is a cloud BYOK edition with local storage, not an entirely offline CLI.

## Slide 8

The goal is simple: give me more room to do the engineering and personal projects I care about. Adversaria is an ongoing project, and today’s Copilot, Spaces and CLI work move it forward. In a demo, I would first show the local meeting context, then a Copilot commitment, then a research or architecture draft in a workspace. The CLI is another way to use the same idea from the terminal. Setup requires the relevant credentials for the selected cloud providers.
