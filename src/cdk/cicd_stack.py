from aws_cdk import (
    IgnoreMode,
    Stack,
    pipelines,
    aws_codebuild as codebuild,
)
import os

from .maple_application_stage import MapleApplication


class CiCdStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            pipeline_name="maple-cicd",
            self_mutation=True,
            docker_enabled_for_synth=True,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    "maple-testimony/lobbying",
                    "main",
                    connection_arn="arn:aws:codestar-connections:us-east-1:968366361019:connection/ba5c5aa4-7567-4051-9c1e-b2d575a1ec74",
                ),
                commands=[
                    "pip install poetry",
                    "poetry lock --check",
                    "poetry install --only synth",
                    "npm install -g aws-cdk",
                    "cdk synth",
                ],
            ),
        )

        pipeline.add_stage(MapleApplication(self, "Prod"))
