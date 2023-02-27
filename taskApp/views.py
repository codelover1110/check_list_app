from django.contrib.auth import get_user_model
from django.core import serializers
from django.shortcuts import render

# Create your views here.
from django.http.response import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer, Customer, UserSerializer, WorkspaceSerializer, TeamSerializer, ListSerializer, RelationshipSerializer, Workspace, List, Relationship_tables, TaskSerializer, Task, Attachments, AttachmentsSerializer, SubmittedList, SubmittedSerializer

from rest_framework.decorators import api_view

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random
import string
from datetime import datetime

from .utils import send_verify_code, send_invite_member, send_approval_notification, send_approval_notification_mailgun

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()



@api_view(['POST'])
def customer_signup(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        if(customer_data['email'] is not None
            and customer_data['first_name'] is not None
            and customer_data['last_name'] is not None
            ):
            customer_db = Customer.objects.filter(email=customer_data['email'])
            if customer_db.exists():
                customer = Customer.objects.get(email=customer_data['email'])
                if ((customer.first_name is None and customer.last_name is None)
                or (customer.first_name == '' and customer.last_name == '')):
                    customer.first_name = customer_data['first_name']
                    customer.last_name = customer_data['last_name']
                    customer.save()
                    return JsonResponse({"status": True, "data": customer_data}, status=status.HTTP_201_CREATED)

                return JsonResponse({"status": False, "message": "Customer already exists."}, status=status.HTTP_400_BAD_REQUEST)
           
            customer_data_serializer = CustomerSerializer(data=customer_data)
            if customer_data_serializer.is_valid():
                customer_data_serializer.save()
                return JsonResponse({"status": True, "data": customer_data_serializer.data}, status=status.HTTP_201_CREATED)

        return JsonResponse({"status": False, "message": "Invaild customer data"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def customer_signin(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        if customer_data['email'] is not None:
            try:
                customer = Customer.objects.get(email=customer_data['email'])
                rand_number = random.randint(1111,9999)
                customer.verify_code = rand_number
                customer.verify_token = get_random_string(16)
                customer.save()
            except:
                return JsonResponse({"status": False, "message": "Invalid User. Please contact the admin user"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                data = {
                    "user": customer_data['email'],
                    "otp": rand_number
                }
                send_verify_code(data)
            except:
                return JsonResponse({"status": False, "message": "Failure Sending Email"}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({
                                "status": True,
                                    "token": customer.verify_token,
                                    "data": {
                                    "email": customer.email,
                                    "first_name": customer.first_name,
                                    "last_name": customer.last_name,
                                    }
                                    }, status=status.HTTP_200_OK)
           
        return JsonResponse({"status": False, "message": "Incorrect email"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def customer_list(request):
    if request.method == 'GET':
        customers= Customer.objects.all()
        customers_serializer = CustomerSerializer(customers, many=True)
        return JsonResponse(customers_serializer.data, safe=False)  



@api_view(['POST'])
def customer_verify(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if data['token'] is not None and data['code'] is not None:
            customer_data = Customer.objects.filter(verify_token=data['token'], verify_code=data['code'])
            if customer_data.exists():
                customer = customer_data.all().values()[0]
                member = Customer.objects.get(email=customer['email'])
                member.verify_token = get_random_string(16)
                member.save()
                return JsonResponse(
                    {
                        "status": True,
                        "token": member.verify_token,
                          "data": {
                            "email": member.email,
                            "first_name": member.first_name,
                            "last_name": member.last_name
                        }
                    },
                    status=status.HTTP_200_OK)
        return JsonResponse({"message": "code or token invalid"}, status=status.HTTP_400_BAD_REQUEST)


def get_random_string(length):
   return (''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=length)))

@api_view(['GET'])
def get_all_workspaces(request):
    if request.method == 'GET':
        workspaces= Workspace.objects.all()
        data = []
        for workspace in workspaces:
            datas_workspace = Relationship_tables.objects.filter(workspace= workspace.id)
            total_lists = []
            total_tasks = []

            for d in datas_workspace:
                if not d.list is None and not d.list.id in total_lists:
                    total_lists.append(d.list.id)

                if not d.task is None and not d.task.id in total_tasks:
                    total_tasks.append(d.task.id)
            
            data.append({
                "workspace_id": workspace.id,
                "workspace_name": workspace.name,
                "total_lists": len(total_lists),
                "total_tasks": len(total_tasks)
            })
        return JsonResponse({"status": True, "data": data}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def get_all_users(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)        
        data = []
        try:
            customer_d = Customer.objects.get(email=json_data['email'])
        except:
            return JsonResponse({"status": False, "message": "User doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)
        relationship_data= Relationship_tables.objects.filter(customer=customer_d.id)

        workspace_ids = []
        
        for r_d in relationship_data:
            return_data = {
                "workspace_id": r_d.workspace.id,
                "workspace_name": r_d.workspace.name,
                "members": []
            }
            if  not r_d.workspace.id in workspace_ids:
                workspace_ids.append( r_d.workspace.id)
                relationship_data = Relationship_tables.objects.filter(workspace=r_d.workspace.id)
                if relationship_data.exists():
                    id_list = []
                    for r_data in relationship_data:
                        invite_status = "Invite Sent"
                        if not r_data.customer is None and not r_data.customer.id in id_list:
                            id_list.append(r_data.customer.id)
                            if r_data.customer.first_name != "":
                                invite_status = "Invite Accepted"
                            else:
                                invite_status = "Invite Sent"
                            return_data["members"].append({
                                "member_id": r_data.customer.id,
                                "member_email": r_data.customer.email,
                                "member_first_name": r_data.customer.first_name,
                                "member_last_name": r_data.customer.last_name,
                                "invite_status": invite_status,
                                "member_role": r_data.role,
                            })
                
                data.append(return_data)

        return JsonResponse({"status": True, "data": data}, status=status.HTTP_201_CREATED)
       


@api_view(['POST'])
def remove_user(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        customer_d = Customer.objects.get(email=json_data['email'])
        try:
            datas = Relationship_tables.objects.filter(workspace=json_data["workspace_id"], customer=customer_d.id)
            if datas.exists():
                for data in datas:
                    data.delete()
                return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"status": False, "message": "User doesn't exist in the current Workspace"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
       

@api_view(['POST'])
def get_workspace_for_user(request):
    if request.method == 'POST':
        workspaces= Workspace.objects.all()
        data = []
        json_data = JSONParser().parse(request)
        try:
            customer_data = Customer.objects.get(email=json_data['email'])
            for workspace in workspaces:
                datas_workspace = Relationship_tables.objects.filter(workspace= workspace.id, customer=customer_data.id)
                if datas_workspace.exists():
                    total_lists = []
                    total_tasks = []
                    members = []
                    members_id = []

                    datas_members = Relationship_tables.objects.filter(workspace= workspace.id)
                    for d_member in datas_members:
                        if not d_member.customer is None and not d_member.customer.id in members_id:
                            members_id.append(d_member.customer.id)
                            members.append({
                                "id": d_member.customer.id,
                                "email": d_member.customer.email,
                                "first_name": d_member.customer.first_name,
                                "last_name": d_member.customer.last_name
                            })

                    for d in datas_members:
                        if not d.list is None and not d.list.id in total_lists:
                            total_lists.append(d.list.id)

                        if not d.task is None and not d.task.id in total_tasks:
                            total_tasks.append(d.task.id)
                    
                    data.append({
                            "workspace_id": workspace.id,
                            "workspace_name": workspace.name,
                            "total_lists": len(total_lists),
                            "total_tasks": len(total_tasks),
                            "members": members
                        })
                    
            return JsonResponse({"status": True, "data": data}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "User doesn't exsit."}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def invite_member_workspace(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        workspace_name = Workspace.objects.filter(name=json_data['workspace_name'])
        if workspace_name.exists():
            for member in json_data['members']:
                customer_db = Customer.objects.filter(email=member['email'])
                if customer_db.exists():
                    customer_id = customer_db[0].id
                else:
                    customer_serialize = CustomerSerializer(data={"email": member['email']})
                    if customer_serialize.is_valid():
                        customer = customer_serialize.save()
                        customer_id = customer.id
                
                relationship_db = Relationship_tables.objects.filter(workspace=workspace_name[0].id, customer=customer_id)
                if relationship_db.exists():
                    continue
                
                relationship_serialize = RelationshipSerializer(data={
                    "customer": customer_id,
                    "workspace": workspace_name[0].id,
                })
                if relationship_serialize.is_valid():
                    relationship_serialize.save()
                    try:
                        now = datetime.now()
                        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        data = {
                            "workspace_name": json_data['workspace_name'],
                            "workspace_id": workspace_name[0].id,
                            "user": member['email'],
                            "date": dt_string
                        }
                        send_invite_member(data)
                    except:
                        pass
                        # return JsonResponse({"status": True, "message": "Failure Sending Email"}, status=status.HTTP_201_CREATED)
                        print(f'{"status": True, "message": "Failure Sending Email"}')

            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_workspace(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            workspace_name = Workspace.objects.filter(name=json_data['workspace_name'])
            if workspace_name.exists():
                return JsonResponse({"status": False, "message": "Workspace already exists."}, status=status.HTTP_400_BAD_REQUEST)
            workspace_db_serialize = WorkspaceSerializer(data={"name": json_data['workspace_name']})
            workspace_id = None
            if workspace_db_serialize.is_valid():
                data = workspace_db_serialize.save()
                workspace_id = data.id
            
            if workspace_id is not None:
                for t_member in json_data['team_members']:
                    customer = Customer.objects.filter(email=t_member['email'])
                    if customer.exists():
                        relationship_serialize = RelationshipSerializer(data={
                            "customer": customer[0].id,
                            "workspace": workspace_id,
                            "role": t_member['role']
                            })
                        if relationship_serialize.is_valid():
                            relationship_serialize.save()

                        # try:
                        #     send_invite_member({"workspace_name": json_data['workspace_name']}, t_member['email'])
                        # except:
                        #     return JsonResponse({"status": True, "message": "Failure Sending Email"}, status=status.HTTP_201_CREATED)
                    else:
                        continue
            
            return JsonResponse({"status": True, "data": {"workspace_id": workspace_id, "workspace_name": json_data['workspace_name']}}, status=status.HTTP_201_CREATED)
        
        except:
            return JsonResponse({"status": False, "message": "Invaild workspace data"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def edit_workspace(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            workspace_data = Workspace.objects.get(id=json_data['workspace_id'])
            workspace_data.name = json_data['workspace_name']
            workspace_data.save()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def remove_workspace(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:

            workspace_data = Workspace.objects.get(id=json_data['workspace_id'])
            workspace_data.delete()

            datas = Relationship_tables.objects.filter(workspace=json_data['workspace_id'])
            if datas.exists():
                for data in datas:
                    data.delete()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_workspace_users(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        workspace_data = Workspace.objects.filter(id=json_data['workspace_id'])
        if workspace_data.exists():  
            relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'])
            return_data = []
            if relationship_data.exists():
                id_list = []
                for data in relationship_data:
                    if not data.customer is None and  not data.customer.id in id_list:
                        id_list.append(data.customer.id)
                        return_data.append({
                            "member_id": data.customer.id,
                            "member_email": data.customer.email,
                            "member_first_name": data.customer.first_name,
                            "member_last_name": data.customer.last_name,
                            "member_role": data.role,
                        })
                return JsonResponse({"status": True, "data": {"workspace_id":json_data['workspace_id'], "workspace_name": relationship_data[0].workspace.name,   "members":return_data}}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"status": True, "data": {"workspace_id":json_data['workspace_id'], "workspace_name": workspace_data[0].name,   "members":return_data}}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            workspace_data = Workspace.objects.filter(id=json_data['workspace_id'])
            if workspace_data.exists():  
                list_db_serialize = ListSerializer(data={"name": json_data['list_name']})
                if list_db_serialize.is_valid():
                    list_data = list_db_serialize.save()
                members = []
                if not 'team_members' in json_data or len(json_data['team_members']) == 0:
                    relationship_serialize = RelationshipSerializer(data={
                        "workspace": json_data['workspace_id'],
                        "list": list_data.id,
                        })
                    if relationship_serialize.is_valid():
                        relationship_serialize.save()

                else:
                    for t_member in json_data['team_members']:
                        customer = Customer.objects.filter(email=t_member['email'])
                        if customer.exists():
                            try:
                                relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], customer=customer[0].id)
                                if not relationship_data.exists():
                                    relationship_serialize = RelationshipSerializer(data={
                                        "customer": customer[0].id,
                                        "workspace": json_data['workspace_id'],
                                        "list": list_data.id,
                                        # "role": relationship_data[0].role
                                        })
                                    if relationship_serialize.is_valid():
                                        relationship_serialize.save()
                                elif relationship_data.exists() and len(relationship_data) > 1:
                                    relationship_serialize = RelationshipSerializer(data={
                                        "customer": customer[0].id,
                                        "workspace": json_data['workspace_id'],
                                        "list": list_data.id,
                                        "role": relationship_data[0].role
                                        })
                                    if relationship_serialize.is_valid():
                                        relationship_serialize.save()
                                else:
                                    relationship_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'], customer=customer[0].id)
                                    if relationship_data.list is not None:
                                        relationship_serialize = RelationshipSerializer(data={
                                            "customer": customer[0].id,
                                            "workspace": json_data['workspace_id'],
                                            "list": list_data.id,
                                            "role": relationship_data.role
                                            })
                                        
                                        if relationship_serialize.is_valid():
                                            relationship_serialize.save()
                                    else:
                                        relationship_data.list = list_data
                                        relationship_data.save()
                                members.append(t_member['email'])
                            except Exception as e:
                                print(e)
                                pass
                        else:
                            continue
                
                return JsonResponse({"status": True, "data": {"list_id": list_data.id, "list_name": list_data.name, "members": members}}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"status": False, "message": "Invaild data"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def edit_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            list_data = List.objects.get(id=json_data["list_id"])
            list_data.name = json_data['list_name']
            list_data.save()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def remove_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:

            list_data = List.objects.get(id=json_data["list_id"])
            list_data.delete()
            
            datas = Relationship_tables.objects.filter(list=json_data['list_id'])
            if datas.exists():
                for data in datas:
                    data.delete()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_list_users(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
        if relationship_workspace_data.exists():
            return_data = []
            id_list = []
            for data in relationship_workspace_data:
                if not data.customer is None and not data.customer.id in id_list:
                    id_list.append(data.customer.id)
                    return_data.append({
                        "member_id": data.customer.id,
                        "member_email": data.customer.email,
                        "member_first_name": data.customer.first_name,
                        "member_last_name": data.customer.last_name,
                        "member_role": data.role,
                    })
            return JsonResponse({"status": True, "data": {
                    "workspace_id":json_data['workspace_id'], 
                    "workspace_name": relationship_workspace_data[0].workspace.name,
                    "list_id": json_data['list_id'],
                    "list_name": relationship_workspace_data[0].list.name,
                    "members":return_data
                }}, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({"status": False, "message": "List user doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def submit_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "workspace_name": json_data['workspace_name'],
                "list_name": json_data['list_name'],
                "list_id": json_data['list_id'],
                "workspace_id": json_data['workspace_id'],
                "submit_user": json_data["submit_user"]["email"],
                "date": dt_string
            }

            send_approval_notification_mailgun(data)
            submitlist_serialize = SubmittedSerializer(data={
                "submit_log": json_data
            })
            if submitlist_serialize.is_valid():
                submitlist_serialize.save()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Failure Sending Email"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def remove_submissions(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            submission = SubmittedList.objects.get(id=json_data["id"])
            submission.delete()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Submissions  doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def get_submitted_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            datas = SubmittedList.objects.all()
            return_data = []
            if datas.exists():
                return_data = []
                for data in datas:
                    if data.submit_log['workspace_id'] == json_data['workspace_id'] and  data.submit_log['list_id'] == json_data['list_id']:
                        tmp_data = data.submit_log
                        tmp_data['id'] = data.id
                        return_data.append(data.submit_log)
            else:
                return JsonResponse({"status": True, "data": []}, status=status.HTTP_201_CREATED)
            return JsonResponse({"status": True, "data": return_data}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def create_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        
        if not "description" in json_data or json_data['description'] == '':
            description_data = None
        else:
            description_data = json_data['description']
        
        if not "frequency" in json_data or json_data['frequency'] == '':
            frequency_data = None
        else:
            frequency_data = json_data['frequency']

        
        if not "dute_date" in json_data or json_data['dute_date'] == '':
            dute_date_data = None
        else:
            dute_date_data = json_data['dute_date']

        
        if not "priority" in json_data or json_data['priority'] == '':
            priority_data = None
        else:
            priority_data = json_data['priority']

        try:
            relation_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
            if relation_data.exists():  
                workspace_name = relation_data[0].workspace.name     
                list_name = relation_data[0].list.name  
                task_db_serialize = TaskSerializer(data={
                    "name": json_data['task_name'],
                    "frequency": frequency_data,
                    "dute_date": dute_date_data,
                    "description": description_data,
                })

                if task_db_serialize.is_valid():
                    task_data = task_db_serialize.save()

                    if 'attachments' in json_data and len(json_data['attachments']) > 0:
                        for att in json_data['attachments']:
                            import base64
                            from django.core.files.base import ContentFile
                            format, imgstr = att['file'].split(';base64,') 
                            ext = format.split('/')[-1] 
                            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                            
                            try:
                                attdb_serialize = AttachmentsSerializer(data={
                                    'task': task_data.id,
                                    'file': data,
                                    'name': att['name']
                                })

                                if attdb_serialize.is_valid():
                                    attdb_serialize.save()
                            except Exception as e:
                                print(e)

                for t_member in json_data['team_members']:
                    customer = Customer.objects.filter(email=t_member['email'])
                    if customer.exists():
                        relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'], customer__isnull=True)
                        if relationship_data.exists():
                            print(333333333333333333333333333333333333)
                            for r_d in relationship_data:
                                r_d.customer = customer[0]
                                r_d.task = task_data
                                r_d.priority = priority_data
                                r_d.save()
                                break
                        
                        else:
                            relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'], customer=customer[0].id, task__isnull=True)   
                            if relationship_data.exists():
                                print(222222222222222222222222222222222, len(relationship_data))
                                for r_d in relationship_data:
                                    r_d.task = task_data
                                    r_d.priority = priority_data
                                    r_d.save()
                                    break
                            else:
                                print(1111111111111111111111)
                                relationship_serialize = RelationshipSerializer(data={
                                    "customer": customer[0].id,
                                    "workspace": json_data['workspace_id'],
                                    "list": json_data['list_id'],
                                    "task": task_data.id,
                                    "role": "user",
                                    "priority": priority_data
                                    })
                                if relationship_serialize.is_valid():
                                    relationship_serialize.save()
                    else:
                        pass
                
                if len(json_data['team_members']) == 0:
                    relationship_serialize = RelationshipSerializer(data={
                        "customer": None,
                        "workspace": json_data['workspace_id'],
                        "list": json_data['list_id'],
                        "task": task_data.id,
                        "role": "user",
                        "priority": priority_data
                        })
                    if relationship_serialize.is_valid():
                        relationship_serialize.save()

                return JsonResponse({"status": True, "data":{
                    "workspace_id": json_data['workspace_id'],
                    "workspace_name": workspace_name,
                    "list_id": json_data['list_id'],
                    "list_name": list_name,
                    "task": {
                        "id": task_data.id,
                        "name": json_data['task_name'],
                        "frequency": frequency_data,
                        "dute_date": dute_date_data,
                        "description": description_data,
                        "priority": priority_data
                    },
                    "members": json_data['team_members']
                }}, status=status.HTTP_201_CREATED)
                
            else:
                return JsonResponse({"status": False, "message": "Workspace or List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            
        except:
            return JsonResponse({"status": False, "message": "Invaild data"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def edit_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
       
        if not "description" in json_data or json_data['description'] == '':
            description_data = None
        else:
            description_data = json_data['description']
        
        if not "frequency" in json_data or json_data['frequency'] == '':
            frequency_data = None
        else:
            frequency_data = json_data['frequency']
        
        if not "dute_date" in json_data or json_data['dute_date'] == '':
            dute_date_data = None
        else:
            dute_date_data = json_data['dute_date']
        
        
        if not "priority" in json_data or json_data['priority'] == '':
            priority_data = None
        else:
            priority_data = json_data['priority']

        try:
            task_data = Task.objects.get(id=json_data["task_id"])
            task_data.name = json_data['task_name']
            task_data.frequency = frequency_data
            task_data.dute_date = dute_date_data
            task_data.description = description_data
            task_data.save()

            if "team_members" in json_data:
                for t_member in json_data["team_members"]:
                    try:
                        customer_db = Customer.objects.get(email=t_member['email'])
                    except Exception as e:
                        print(e)
                        continue

                    try:
                        t_rel = Relationship_tables.objects.get(task=json_data['task_id'], customer=customer_db.id)
                        t_rel.priority = priority_data
                        t_rel.save()
                    except:
                        relationship_serialize = RelationshipSerializer(data={
                            "customer": customer_db.id,
                            "workspace": json_data['workspace_id'],
                            "list": json_data['list_id'],
                            "task": task_data.id,
                            "role": "user",
                            "priority": priority_data
                            })
                        if relationship_serialize.is_valid():
                            relationship_serialize.save()

            try:
                if 'attachments' in json_data and len(json_data['attachments']) > 0:
                    att_datas = Attachments.objects.filter(task=json_data['task_id'])
                    db_data = []
                    attr_data = []
                   
                    if att_datas.exists():
                        for att_d in att_datas:
                            db_data.append(att_d.name)

                    for att in json_data['attachments']:
                        attr_data.append(att['name'])
                        if not att['name'] in db_data:
                            import base64
                            from django.core.files.base import ContentFile
                            format, imgstr = att['file'].split(';base64,') 
                            ext = format.split('/')[-1] 
                            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)                     
                            try:
                                attdb_serialize = AttachmentsSerializer(data={
                                    'task': task_data.id,
                                    'file': data,
                                    'name': att['name']
                                })

                                if attdb_serialize.is_valid():
                                    attdb_serialize.save()
                                    
                            except Exception as e:
                                print(e)
                    
                    if att_datas.exists():
                        for att_d in att_datas:
                            if not att_d.name in attr_data:
                                att_d.delete()

            except Exception as e:
                print(e)
                return JsonResponse({"status": False, "message": "Failing file upload"}, status=status.HTTP_400_BAD_REQUEST)


            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Task doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def remove_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            task_data = Task.objects.get(id=json_data["task_id"])
            task_data.delete()
            
            datas = Relationship_tables.objects.filter(task=json_data['task_id'])
            if datas.exists():
                for data in datas:
                    data.delete()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False, "message": "Task doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_task_by_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        # try:
        relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'],
                                                                        list=json_data['list_id'],
                                                                    )
        
        daily_list = []
        weekly_list = []
        monthly_list = []
        no_option = []
        task_list = []
        members = []
        members_id = []
        datas_members = Relationship_tables.objects.filter(workspace=json_data['workspace_id'])
        for d_member in datas_members:
            if not d_member.customer is None and not d_member.customer.id in members_id:
                members_id.append(d_member.customer.id)
                members.append({
                    "id": d_member.customer.id,
                    "email": d_member.customer.email,
                    "first_name": d_member.customer.first_name,
                    "last_name": d_member.customer.last_name,
                    "role": d_member.role
                })

        for data in relationship_workspace_data:
            if data.task is not None and not data.task.id in task_list:
                task_list.append(data.task.id)
                file_attachment = []
                att_db_data = Attachments.objects.filter(task=data.task.id)     
                if att_db_data.exists():
                    for att_d in att_db_data:
                        file_attachment.append({
                            "file": att_d.file.name,
                            "name": att_d.name
                        })
                task_ms = []
                r_datasets = Relationship_tables.objects.filter(task=data.task.id)
                for r_d in r_datasets:
                    if r_d.customer is not None and not r_d.customer.email in task_ms:
                        task_ms.append({"email": r_d.customer.email})
                
                data_detail = {   
                    "check_status": data.check_status,
                    "task": {
                        "id": data.task.id,
                        "name":  data.task.name,
                        "frequency": data.task.frequency,
                        "dute_date": data.task.dute_date,
                        "description": data.task.description,
                        "priority": data.priority,
                        "attachments": file_attachment
                    },
                     "members": task_ms     
                }


                if data.task.frequency == 'daily':
                    daily_list.append(data_detail)
                elif data.task.frequency == 'weekly':
                    weekly_list.append(data_detail)
                elif data.task.frequency == 'montly':
                    monthly_list.append(data_detail)
                else:
                    no_option.append(data_detail)

        return JsonResponse({"status": True, "data": {
                                                "workspace_id": json_data['workspace_id'],
                                                "workspace_name": relationship_workspace_data[0].workspace.name,
                                                "list_id": json_data['list_id'],
                                                "list_name": relationship_workspace_data[0].list.name,
                                                "daily":daily_list,
                                                "weekly":weekly_list,
                                                "monthly":monthly_list,
                                                "no_option": no_option,
                                                "members": members
                                            }}, status=status.HTTP_201_CREATED)
        # except:
        #     return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def remove_task(request):
#     if request.method == 'POST':
#         json_data = JSONParser().parse(request)
#         try:
#             for t_member in json_data['members']:
#                 try:
#                     relationship_workspace_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'],
#                                                                                     list=json_data['list_id'],
#                                                                                     task=json_data['task_id'],
#                                                                                     customer=t_member
#                                                                                     )
#                     relationship_workspace_data.delete()
#                 except:
#                     pass

#             return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

#         except:
#             return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_list(request, pk):
    if request.method == 'GET':
        datas = Relationship_tables.objects.filter(workspace=pk)
        if datas.exists():
            return_data = []
            id_list = []
            for data in datas:
                if not data.list is None and not data.list.id in id_list:
                    tasks_relationship = Relationship_tables.objects.filter(workspace=pk, list=data.list.id).exclude(task__isnull=True)
                    total_tasks = []
                    success_tasks = []
                    for t_data in tasks_relationship:
                        if not t_data.task.id in total_tasks:
                            total_tasks.append(t_data.task.id)
                            if t_data.check_status == True:
                                success_tasks.append(t_data.task.id)

                    # success_tasks = Relationship_tables.objects.filter(workspace=pk, list=data.list.id, priority='success').count()
                    return_data.append({
                        "list_id": data.list.id,
                        "list_name": data.list.name,
                        "total_tasks": len(total_tasks),
                        "success_tasks": len(success_tasks)
                    })
                    id_list.append(data.list.id)
        else:
            return JsonResponse({"status": True, "data": []}, status=status.HTTP_201_CREATED)
        return JsonResponse({"status": True, "data": return_data}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def check_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'],
                                                                                    list=json_data['list_id'],
                                                                                    task=json_data['task_id']
                                                                            )
            for r_data in relationship_workspace_data:
                r_data.check_status = True
                r_data.save()
            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

        except:
            return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def uncheck_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'],
                                                                                    list=json_data['list_id'],
                                                                                    task=json_data['task_id']
                                                                                    )
            for r_data in relationship_workspace_data:
                r_data.check_status = False
                r_data.save()

            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

        except:
            return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def uncheck_task_frequency(request, frequency):
    if request.method == 'GET':
        datas = Relationship_tables.objects.all()
        for data in datas:
            if not data.task is None and data.task.frequency == frequency:
                data.check_status = 0
                data.save()
        return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def check_task_frequency(request, frequency):
    if request.method == 'GET':
        datas = Relationship_tables.objects.all()
        for data in datas:
            if not data.task is None and data.task.frequency == frequency:
                data.check_status = 1
                data.save()
        return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def check_off(request):
    if request.method == 'POST': 
        json_data = JSONParser().parse(request)
        datas = Relationship_tables.objects.all()
        for data in datas:
            if json_data['frequency'] == 'no_option' and not data.task is None and data.task.frequency is None and data.workspace.id == json_data['workspace_id'] and data.list.id == json_data['list_id']:
                if json_data['check_status'] == False:
                    data.check_status = 0
                else:
                    data.check_status = 1
                data.save()

            elif not data.task is None and data.task.frequency == json_data['frequency'] and data.workspace.id == json_data['workspace_id'] and data.list.id == json_data['list_id']:
                if json_data['check_status'] == False:
                    data.check_status = 0
                else:
                    data.check_status = 1
                data.save()
        return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def get_single_workspace_id(request):
    if request.method == 'POST': 
        json_data = JSONParser().parse(request)
        number_list = []
        number_of_task = []
        number_of_successs_task  = []
        workspace_data = Workspace.objects.filter(id=json_data['workspace_id'])
        if workspace_data.exists():  
            relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'])
            if relationship_workspace_data.exists():
                for data in relationship_workspace_data:
                    if not data.list is None and not data.list.id in number_list:
                        number_list.append(data.list.id)
                    if data.task is not None and not data.task.id in number_of_task:
                        number_of_task.append(data.task.id)
                        if data.check_status == True:
                            number_of_successs_task.append(data.task.id)
                
            return JsonResponse({"status": True, "data": {
                                    "workspace_id": json_data['workspace_id'],
                                    "workspace_name": workspace_data[0].name,
                                    "number_of_list": len(number_list),
                                    "number_of_task": len(number_of_task),
                                    "number_of_successs_task": len(number_of_successs_task)
                                }}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": False, "message": "Workspace doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_single_list_id(request):
    if request.method == 'POST': 
        json_data = JSONParser().parse(request)
        number_of_task = []
        number_of_successs_task  = []
        list_data = List.objects.filter(id=json_data['list_id'])
        if list_data.exists():  
            relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
            if relationship_workspace_data.exists():
                for data in relationship_workspace_data:
                    if data.task is not None and not data.task.id in number_of_task:
                        number_of_task.append(data.task.id)
                        # if data.priority == 'success':
                        if data.check_status == True:
                            number_of_successs_task.append(data.task.id)
            
            if not relationship_workspace_data.exists():
                return JsonResponse({"status": False, "message": "Invalid List"}, status=status.HTTP_400_BAD_REQUEST)
                
            return JsonResponse({"status": True, "data": {
                                    "workspace_id": json_data['workspace_id'],
                                    "workspace_name": relationship_workspace_data[0].workspace.name,
                                    "list_id": json_data['list_id'],
                                    "list_name": list_data[0].name,
                                    "number_of_task": len(number_of_task),
                                    "number_of_successs_task": len(number_of_successs_task)
                                }}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": False, "message": "List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_single_task_id(request):
    if request.method == 'POST': 
        json_data = JSONParser().parse(request)
        relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'], task=json_data['task_id'])
        members = []
        if relationship_workspace_data.exists():
            for data in relationship_workspace_data:
                members.append({
                    "id": data.customer.id,
                    "email": data.customer.email,
                    "first_name": data.customer.first_name,
                    "last_name": data.customer.last_name
                })
            
            file_attachment = []
            att_db_data = Attachments.objects.filter(task=data.task.id)     
            if att_db_data.exists():
                for att_d in att_db_data:
                    file_attachment.append({
                        "file": att_d.file.name,
                        "name": att_d.name
                    })

            return JsonResponse({"status": True, "data": {
                    "workspace_id": data.workspace.id,
                    "workspace_name": data.workspace.name,
                    "list_id": data.list.id,
                    "list_name": data.list.name,
                    "task_detail": {
                        "task_id": data.task.id,
                        "task_name": data.task.name,
                        "frequency": data.task.frequency,
                        "attachments": file_attachment,
                        "dute_date": data.task.dute_date,
                        "description": data.task.description,
                        "priority": data.priority,
                    },
                    "members": members
            }}, status=status.HTTP_201_CREATED)
            
               
        else:
            return JsonResponse({"status": False, "message": "Task doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

