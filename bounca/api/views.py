


import rest_framework
from rest_framework import generics, permissions
from .serializers import CertificateSerializer
from ..x509_pki.models import Certificate
from .mixins import TrapDjangoValidationErrorCreateMixin
from idlelib.ClassBrowser import file_open

class APIPageNumberPagination(rest_framework.pagination.PageNumberPagination):
    page_size=10

class CertificateListView(TrapDjangoValidationErrorCreateMixin, generics.ListCreateAPIView):
    model = Certificate
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [
#        permissions.DjangoObjectPermissions
#
# Django Guardian configure
        permissions.IsAuthenticated
    ]
    search_fields = ('shortname','name',) 
    pagination_class = APIPageNumberPagination
    filter_fields = ('type', 'parent',)

class CertificateInstanceView(generics.RetrieveDestroyAPIView):
    model = Certificate
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [
#        permissions.DjangoObjectPermissions
#
# Django Guardian configure
        permissions.IsAuthenticated
    ]

from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseNotFound

class CertificateInfoView(View):
    def get(self, request, pk, format=None):
        cert=None
        try:
            cert = Certificate.objects.get(pk=pk);
        except:
            return HttpResponseNotFound("File not found")
        info = cert.get_certificate_info()
        return HttpResponse(info)


from django.conf import settings
import io
import os
import zipfile

from ..x509_pki.models import CertificateTypes
from django.conf import settings

class CertificateFilesView(View):

    def generate_path(self, certificate):
        prefix_path=""
        if certificate.parent and certificate.pk != certificate.parent.pk:
            prefix_path=self.generate_path(certificate.parent)
        return prefix_path + "/" + str(certificate.shortname)

    def get_root_cert_path(self, certificate):
        if certificate.parent and certificate.pk != certificate.parent.pk:
            return self.get_root_cert_path(certificate.parent)
        else:
            root_cert_path = settings.CA_ROOT + "/" + str(certificate.shortname) + "/certs/" + str(certificate.shortname) + ".cert.pem" 
            return root_cert_path

    def read_file(self, filename):
        with open(filename,'rb') as f:
            file_content=f.read()
            return file_content
    
    def get(self, request, pk, format=None):
        cert=None
        try:
            cert = Certificate.objects.get(pk=pk);
        except:
            return HttpResponseNotFound("File not found")
        
        key_path = settings.CA_ROOT + self.generate_path(cert)
        if cert.type is CertificateTypes.ROOT:
            orig_file=key_path + "/certs/" + cert.shortname + ".cert.pem" 
            try:
                file_content=self.read_file(orig_file)
                filename="%s.pem" % (cert.shortname)
                response = HttpResponse(file_content, content_type='text/plain')
                response['Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        if cert.type is CertificateTypes.INTERMEDIATE:
            orig_file=key_path + "/certs/" + cert.shortname + "-chain.cert.pem" 
            try:
                file_content=self.read_file(orig_file)
                filename="%s-chain.pem" % (cert.shortname)
                response = HttpResponse(file_content, content_type='text/plain')
                response['Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        key_path = settings.CA_ROOT + self.generate_path(cert.parent)
        if cert.type is CertificateTypes.SERVER_CERT:
            try:
                root_cert_file=self.get_root_cert_path(cert)
                root_cert_file_content=self.read_file(root_cert_file)
                cert_file=key_path + "/certs/server/" + cert.shortname + "-chain.cert.pem" 
                cert_file_content=self.read_file(cert_file)
                key_file=key_path + "/private/server/" + cert.shortname + ".key.pem" 
                key_file_content=self.read_file(key_file)
    
                
                zipped_file = io.BytesIO()
                with zipfile.ZipFile(zipped_file, 'w') as f:
                    f.writestr(cert.shortname + "-rootca.pem", root_cert_file_content)
                    f.writestr(cert.shortname + "-chain.pem", cert_file_content)
                    f.writestr(cert.shortname + ".key", key_file_content)
                zipped_file.seek(0)
    
                filename="%s.servercert.zip" % (cert.shortname)
                response = HttpResponse(zipped_file, content_type='application/octet-stream')
                response['Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        if cert.type is CertificateTypes.CLIENT_CERT:
            try:
                root_cert_file=self.get_root_cert_path(cert)
                root_cert_file_content=self.read_file(root_cert_file)
                cert_file=key_path + "/certs/client/" + cert.shortname + "-chain.cert.pem" 
                cert_file_content=self.read_file(cert_file)
                key_file=key_path + "/private/client/" + cert.shortname + ".key.pem" 
                key_file_content=self.read_file(key_file)
    
                
                zipped_file = io.BytesIO()
                with zipfile.ZipFile(zipped_file, 'w') as f:
                    f.writestr(cert.shortname + "-rootca.pem", root_cert_file_content)
                    f.writestr(cert.shortname + "-chain.pem", cert_file_content)
                    f.writestr(cert.shortname + ".key", key_file_content)
                zipped_file.seek(0)
    
                filename="%s.clientcert.zip" % (cert.shortname)
                response = HttpResponse(zipped_file, content_type='application/octet-stream')
                response['Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")        
        return HttpResponseNotFound("File not found")