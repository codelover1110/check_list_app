from django.contrib.auth import get_user_model
from django.core import serializers
from django.shortcuts import render

# Create your views here.
from django.http.response import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer, Customer, UserSerializer, WorkspaceSerializer, TeamSerializer, ListSerializer, RelationshipSerializer, Workspace, List, Relationship_tables, TaskSerializer, Task

from rest_framework.decorators import api_view

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random
import string
from datetime import datetime

from .utils import send_email, send_verify_code, send_email_teammember, send_welcome_email, send_invite_member

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
                send_verify_code(rand_number, customer_data['email'])
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
                        "token": member.verify_token
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
            data.append({
                "workspace_id": workspace.id,
                "workspace_name": workspace.name
            })
        return JsonResponse({"status": True, "data": data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def invite_member_workspace(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        workspace_name = Workspace.objects.filter(name=json_data['workspace_name'])
        if workspace_name.exists():
            customer_db = Customer.objects.filter(email=json_data['member_email'])
            if customer_db.exists():
               customer_id = customer_db[0].id
            else:
                customer_serialize = CustomerSerializer(data={"email": json_data['member_email']})
                if customer_serialize.is_valid():
                    customer = customer_serialize.save()
                    customer_id = customer.id
            
            relationship_db = Relationship_tables.objects.filter(workspace=workspace_name[0].id, customer=customer_id)
            if relationship_db.exists():
                return JsonResponse({"status": False, "message": "The user already was invited."}, status=status.HTTP_400_BAD_REQUEST)
            
            relationship_serialize = RelationshipSerializer(data={
                            "customer": customer_id,
                            "workspace": workspace_name[0].id,
                            })
            if relationship_serialize.is_valid():
                relationship_serialize.save()
                try:
                    send_invite_member({"workspace_name": json_data['workspace_name']}, json_data['member_email'])
                except:
                    return JsonResponse({"status": True, "message": "Failure Sending Email"}, status=status.HTTP_201_CREATED)
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
def get_workspace_users(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'])
        if relationship_data.exists():
            return_data = []
            id_list = []
            for data in relationship_data:
                if not data.customer.id in id_list:
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
def get_list_users(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
        if relationship_workspace_data.exists():
            return_data = []
            id_list = []
            for data in relationship_workspace_data:
                if not data.customer.id in id_list:
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
            relation_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
            if relation_data.exists():  
                frequency_list = ["daily","weekly", "monthly"]
                for frequency_data in frequency_list:
                    for work_data in json_data[frequency_data]:
                        try:
                            relationship_data = Relationship_tables.objects.get(
                                workspace=json_data['workspace_id'],
                                customer=work_data["member"]["id"], 
                                task=work_data["task"]["id"], 
                                list=json_data['list_id'])                           
                            
                            relationship_data.priority = work_data["task"]["priority"]
                            relationship_data.save()
                        except Exception as e:
                            print(e)
                            pass
                
                return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)
            return JsonResponse({"status": False, "message": "Workspace or List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return JsonResponse({"status": False, "message": "Invaild data"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            relation_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], list=json_data['list_id'])
            if relation_data.exists():  
                task_db_serialize = TaskSerializer(data={
                    "name": json_data['task_name'],
                    "frequency": json_data['frequency'],
                    "attachments": "attachments",
                    "dute_date": json_data['dute_date'],
                    "description": json_data['description'],
                })

                if task_db_serialize.is_valid():
                    task_data = task_db_serialize.save()
                customer_data = []
                for t_member in json_data['team_members']:
                    customer = Customer.objects.filter(email=t_member['email'])
                    if customer.exists():
                        try:
                            relationship_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'], customer=customer[0].id, list=json_data['list_id'])   
                            workspace_name = relationship_data[0].workspace.name                        
                            list_name = relationship_data[0].list.name  
                            customer_data.append({
                                "id": customer[0].id,
                                "email": customer[0].email,
                                "first_name": customer[0].first_name,
                                "last_name": customer[0].last_name,
                            })     

                            if relationship_data.exists() and len(relationship_data) > 1:
                                relationship_serialize = RelationshipSerializer(data={
                                    "customer": customer[0].id,
                                    "workspace": json_data['workspace_id'],
                                    "list": json_data['list_id'],
                                    "task": task_data.id,
                                    "role": relationship_data[0].role
                                    })
                                if relationship_serialize.is_valid():
                                    relationship_serialize.save()

                            else:
                                relationship_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'], customer=customer[0].id, list=json_data['list_id'])                           

                                if relationship_data.task is not None:
                                    relationship_serialize = RelationshipSerializer(data={
                                        "customer": customer[0].id,
                                        "workspace": json_data['workspace_id'],
                                        "list": json_data['list_id'],
                                        "task": task_data.id,
                                        "role": relationship_data.role
                                        })
                                    if relationship_serialize.is_valid():
                                        relationship_serialize.save()
                                else:  
                                    relationship_data.task = task_data
                                    relationship_data.save()
                        except Exception as e:
                            print(e)
                            pass
                    else:
                        pass
                return JsonResponse({"status": True, "data":{
                    "workspace_id": json_data['workspace_id'],
                    "workspace_name": workspace_name,
                    "list_id": json_data['list_id'],
                    "list_name": list_name,
                    "task": {
                        "id": task_data.id,
                        "name": json_data['task_name'],
                        "frequency": json_data['frequency'],
                        "attachments": "attachments",  
                        "dute_date": json_data['dute_date'],
                        "description": json_data['description'],
                    },
                    "members": customer_data

                }}, status=status.HTTP_201_CREATED)
                
            else:
                return JsonResponse({"status": False, "message": "Workspace or List doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
                
        except:
            return JsonResponse({"status": False, "message": "Invaild data"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_task_by_list(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            relationship_workspace_data = Relationship_tables.objects.filter(workspace=json_data['workspace_id'],
                                                                            list=json_data['list_id'],
                                                                        )
            
            daily_list = []
            weekly_list = []
            monthly_list = []
            for data in relationship_workspace_data:
                if data.task is not None:
                    data_detail = {   
                        "check_status": data.check_status,
                        "task": {
                            "id": data.task.id,
                            "name":  data.task.name,
                            "frequency": data.task.frequency,
                            "attachments": "attachments",  
                            "dute_date": data.task.dute_date,
                            "description": data.task.description,
                            "priority": data.priority,
                        },
                        "member": {
                            "id": data.customer.id,
                            "email": data.customer.email,
                            "first_name": data.customer.first_name,
                            "last_name": data.customer.last_name,
                            "role": data.role,
                        }
                    }

                    if data.task.frequency == 'daily':
                        daily_list.append(data_detail)
                    elif data.task.frequency == 'weekly':
                        weekly_list.append(data_detail)
                    elif data.task.frequency == 'montly':
                        monthly_list.append(data_detail)

            return JsonResponse({"status": True, "data": {
                                                    "workspace_id": json_data['workspace_id'],
                                                    "workspace_name": relationship_workspace_data[0].workspace.name,
                                                    "list_id": json_data['list_id'],
                                                    "list_name": relationship_workspace_data[0].list.name,
                                                    "daily":daily_list,
                                                    "weekly":weekly_list,
                                                    "monthly":monthly_list,
                                                }}, status=status.HTTP_201_CREATED)
        except:
            return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def remove_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            for t_member in json_data['members']:
                try:
                    relationship_workspace_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'],
                                                                                    list=json_data['list_id'],
                                                                                    task=json_data['task_id'],
                                                                                    customer=t_member
                                                                                    )
                    relationship_workspace_data.delete()
                except:
                    pass

            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

        except:
            return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_list(request, pk):
    if request.method == 'GET':
        datas = Relationship_tables.objects.filter(workspace=pk)
        if datas.exists():
            return_data = []
            id_list = []
            for data in datas:
                if not data.list is None and not data.list.id in id_list:
                    return_data.append({
                        "list_id": data.list.id,
                        "list_name": data.list.name
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
            for t_member in json_data['members']:
                try:
                    relationship_workspace_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'],
                                                                                    list=json_data['list_id'],
                                                                                    task=json_data['task_id'],
                                                                                    customer=t_member
                                                                                    )
                    relationship_workspace_data.check_status = True
                    relationship_workspace_data.save()
                except:
                    pass

            return JsonResponse({"status": True}, status=status.HTTP_201_CREATED)

        except:
            return JsonResponse({"status": False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def uncheck_task(request):
    if request.method == 'POST':
        json_data = JSONParser().parse(request)
        try:
            for t_member in json_data['members']:
                try:
                    relationship_workspace_data = Relationship_tables.objects.get(workspace=json_data['workspace_id'],
                                                                                    list=json_data['list_id'],
                                                                                    task=json_data['task_id'],
                                                                                    customer=t_member
                                                                                    )
                    relationship_workspace_data.check_status = False
                    relationship_workspace_data.save()
                except:
                    pass

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

