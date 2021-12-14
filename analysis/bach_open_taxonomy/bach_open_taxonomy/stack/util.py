"""
Copyright 2021 Objectiv B.V.
"""
from bach_open_taxonomy.stack.basic_features import BasicFeatures
from bach_open_taxonomy.stack.extracted_contexts import ExtractedContexts
from bach_open_taxonomy.stack.sessionized_data import SessionizedData
from sql_models.model import SqlModel


def basic_feature_model(session_gap_seconds=1800) -> SqlModel:
    """ Give a linked BasicFeatures model"""
    extracted_contexts = ExtractedContexts()
    return BasicFeatures.build(
        sessionized_data=SessionizedData(
            session_gap_seconds=session_gap_seconds,
            extracted_contexts=extracted_contexts
        )
    )


def sessionized_data_model(session_gap_seconds=1800) -> SqlModel:
    """ Give a linked SessionizedData model"""
    extracted_contexts = ExtractedContexts()
    return SessionizedData.build(
            session_gap_seconds=session_gap_seconds,
            extracted_contexts=extracted_contexts
        )
