import sys

from tests.test_auth import (
    test_password_hashing,
    test_jwt_token_generation_and_decoding
)
from tests.test_auth_security import (
    test_admin_vs_supervisor_authorization,
    test_refresh_token_rotation,
    test_login_rate_limiting
)
from tests.test_phase4 import (
    test_unit_discrepancy_service_consecutive_streak,
    test_extra_fields_pydantic_rejection,
    test_discrepancy_edge_case_no_ai_count,
    test_disallowed_file_upload_failure_case,
    test_integration_endpoints_and_auth_failures
)
from tests.test_phase6_ai import (
    test_unit_confidence_threshold_logic,
    test_edge_case_empty_scene_zero_violations,
    test_failure_case_corrupted_unreadable_video,
    test_end_to_end_full_pipeline_demo
)
from tests.test_real_yolo_detection import test_real_yolov8_inference
from tests.test_phase7_advanced import (
    test_integration_three_consecutive_mismatches_escalation,
    test_integration_single_mismatch_no_escalation,
    test_security_supervisor_forbidden_from_admin_escalation_endpoint,
    test_ai_hazard_categorization
)
from tests.test_phase8_security_performance import (
    test_security_jwt_tampering_rejection,
    test_security_sqli_parameterization,
    test_performance_concurrent_dashboard_requests
)

def run_phase8_full_test_suite():
    print("\n==========================================================================")
    print("      SITE INTEL AI: FULL PHASE 8 VERIFICATION & TEST SUITE RUNNER       ")
    print("==========================================================================")

    # 1. Auth & Password Security
    print("\n>>> EXECUTION BLOCK 1: AUTHENTICATION, JWT & SECURITY ROTATION")
    test_password_hashing()
    test_jwt_token_generation_and_decoding()
    test_admin_vs_supervisor_authorization()
    test_refresh_token_rotation()
    test_login_rate_limiting()

    # 2. Phase 4 Core APIs & Business Logic
    print("\n>>> EXECUTION BLOCK 2: BACKEND CORE APIS, PYDANTIC STRICTNESS & DISCREPANCY LOGIC")
    test_unit_discrepancy_service_consecutive_streak()
    test_extra_fields_pydantic_rejection()
    test_discrepancy_edge_case_no_ai_count()
    test_disallowed_file_upload_failure_case()
    test_integration_endpoints_and_auth_failures()

    # 3. Phase 6 AI Computer Vision Pipeline
    print("\n>>> EXECUTION BLOCK 3: AI COMPUTER VISION PIPELINE & REAL HTTP DB INGESTION")
    test_unit_confidence_threshold_logic()
    test_edge_case_empty_scene_zero_violations()
    test_failure_case_corrupted_unreadable_video()
    test_end_to_end_full_pipeline_demo()

    # 4. Phase 6 Real Un-Mocked YOLOv8 Model Inference
    print("\n>>> EXECUTION BLOCK 4: REAL UN-MOCKED YOLOv8 MODEL INFERENCE")
    test_real_yolov8_inference()

    # 5. Phase 7 Advanced Features & Escalations
    print("\n>>> EXECUTION BLOCK 5: ADVANCED FEATURES & ADMIN ESCALATION NOTIFICATIONS")
    test_integration_three_consecutive_mismatches_escalation()
    test_integration_single_mismatch_no_escalation()
    test_security_supervisor_forbidden_from_admin_escalation_endpoint()
    test_ai_hazard_categorization()

    # 6. Phase 8 System Security & Performance Tests
    print("\n>>> EXECUTION BLOCK 6: SYSTEM SECURITY (JWT TAMPERING, SQLi) & PERFORMANCE")
    test_security_jwt_tampering_rejection()
    test_security_sqli_parameterization()
    test_performance_concurrent_dashboard_requests()

    print("\n==========================================================================")
    print("     ALL PHASE 8 TESTS COMPLETED SUCCESSFULLY WITH ZERO ERRORS!          ")
    print("==========================================================================")

def test_run_all_phase8_tests():
    run_phase8_full_test_suite()

if __name__ == "__main__":
    run_phase8_full_test_suite()
