from rest_framework import serializers

class CourseSerializer(serializers.Serializer):
    """
    Serializer for course data from elearning.univ-bba.dz
    """
    name = serializers.CharField()
    url = serializers.URLField(allow_null=True)
    image = serializers.URLField(allow_null=True)
    summary = serializers.CharField(allow_blank=True)
    teachers = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class DepartmentSerializer(serializers.Serializer):
    """
    Serializer for department data from elearning.univ-bba.dz
    """
    id = serializers.CharField()
    name = serializers.CharField()
    url = serializers.URLField()


class LinkSerializer(serializers.Serializer):
    """
    Serializer for link data with 'aalink' class
    """
    text = serializers.CharField()
    href = serializers.URLField()
    course_id = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class ResourceSerializer(serializers.Serializer):
    """
    Serializer for course resource data including PDF links
    """
    resource_name = serializers.CharField()
    resource_url = serializers.URLField()
    pdf_url = serializers.URLField(allow_null=True)
    pdf_name = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False)
