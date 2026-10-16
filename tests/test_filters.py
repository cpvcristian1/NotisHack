import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_is_ai_topic_true():
    import filters
    h = {"title": "AI Hackathon", "description": "machine learning"}
    assert filters.is_ai_topic(h) is True

def test_is_ai_topic_false():
    import filters
    h = {"title": "Web Dev Hack", "description": "build websites"}
    assert filters.is_ai_topic(h) is False

def test_is_ai_topic_no_false_positive():
    import filters
    h = {"title": "Email Campaign", "description": "said hello"}
    assert filters.is_ai_topic(h) is False

def test_is_location_match_online():
    import filters
    h = {"location": "Online"}
    assert filters.is_location_match(h) is True

def test_is_location_match_vigo():
    import filters
    h = {"location": "Vigo, Spain"}
    assert filters.is_location_match(h) is True

def test_is_location_match_other():
    import filters
    h = {"location": "Berlin, Germany"}
    assert filters.is_location_match(h) is False

def test_allows_ai_coding_true():
    import filters
    h = {"description": "AI tools allowed, use any tools you want"}
    assert filters.allows_ai_coding(h) is True

def test_allows_ai_coding_false():
    import filters
    h = {"description": "no AI generated code, must write own code"}
    assert filters.allows_ai_coding(h) is False

def test_allows_ai_coding_unspecified():
    import filters
    h = {"description": "build something cool"}
    assert filters.allows_ai_coding(h) is True

def test_apply_all():
    import filters
    h = {"title": "AI Hack", "location": "Online", "description": "AI tools allowed"}
    assert filters.apply_all(h) is True
    h2 = {"title": "Web Hack", "location": "Online", "description": "use any tools you want"}
    assert filters.apply_all(h2) is False