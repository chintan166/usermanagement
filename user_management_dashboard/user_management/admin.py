from django.contrib import admin
from .models import AttendanceRecord,Resume,BlogPost,Post,Message,Quiz,Subtopic,Question,Answer,UserProfile,Topic,Video,Project, Submission,CustomUser

class UserProfileAdmin(admin.ModelAdmin):
    # List the fields to be displayed in the admin change list page (list view)
    list_display = ('user', 'area_of_interest')  # Add more fields here if needed

    # Add the fields to be displayed in the form (edit view)
    fieldsets = (
        (None, {
            'fields': ('user', 'area_of_interest'),
        }),
    )
    
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username','role','education','college_name','address','sex','is_approved')
    
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question','text')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz','text')
    
    

admin.site.register(AttendanceRecord)
admin.site.register(Quiz)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer,AnswerAdmin)
admin.site.register(Topic)
admin.site.register(Video)
admin.site.register(Project)
admin.site.register(Submission)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Subtopic)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Resume)
admin.site.register(BlogPost)