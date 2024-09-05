from django.contrib import admin
from django.db.models.aggregates import Count
from . import models

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
     
    fields = ['project_name', 'afa_case_id', 'line_name', 'no_of_terminals', 'notes']
    
    # readonly_fields = ['project_name']
    
    # prepopulated_fields = {
    #     'project_name': ['line_name']
    # }
    
    list_display = ['project_name', 'afa_case_id', 'line_name', 'created_on', 'files_count']
    list_filter = ['afa_case_id', 'line_name', 'created_on']
    list_per_page = 20
    search_fields = ['afa_case_id', 'line_name', 'project_name']
    
    @admin.display(ordering='files_count')
    def files_count(self, project):
        return project.files_count

    def get_queryset(sefl, request):
        return super().get_queryset(request).annotate(files_count= Count('files'))

    # watch and follow create custom action video for setting up action to delete all projects above an age.


    # @admin.display(ordering='created_on')
    # def project_age(self, project):
    #     # dt = datetime.now() + timedelta(days=30)
    #     # created_date = datetime.fromtimestamp(project.created_on)
        
    #     if created_date < dt:
    #         return 'Old'
    #     return 'OK'