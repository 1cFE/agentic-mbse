package SI {
    part def ProjectType {
        attribute project_value : ScalarValues::Real = 1.0;
    }
}

package SemanticEvidenceConsumer {
    private import SI::*;

    part project_part : ProjectType {
        attribute copied_value : ScalarValues::Real = project_value;
    }
}
