# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-28 16:48
from __future__ import unicode_literals

import bounca.x509_pki.models
from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('R', 'Root CA Certificate'), ('I', 'Intermediate CA Certificate'), ('S', 'Server Certificate'), ('C', 'Client Certificate'), ('O', 'OCSP Signing Certificate')], max_length=1)),
                ('shortname', models.CharField(help_text='Short name to identify your key.', max_length=128, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z\\_\\.]*$', 'Only alphanumeric characters and [_.] are allowed.')], verbose_name='Short Name')),
                ('name', models.CharField(blank=True, help_text='Long name of your key, if not set will be equal to your shortname + CommonName.', max_length=128, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ ]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')])),
                ('crl_distribution_url', models.URLField(blank=True, help_text='Base URL for certificate revocation list (CRL)', null=True, verbose_name='CRL distribution url')),
                ('ocsp_distribution_host', models.URLField(blank=True, help_text='Host URL for Online Certificate Status Protocol (OCSP)', null=True, verbose_name='OCSP distribution host')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('expires_at', models.DateField(help_text='Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year. Allowed date format: yyyy-mm-dd.', validators=[bounca.x509_pki.models.validate_in_future])),
                ('revoked_at', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('revoked_uuid', models.UUIDField(default='00000000000000000000000000000001')),
            ],
            options={
                'db_table': 'bounca_certificate',
            },
        ),
        migrations.CreateModel(
            name='DistinguishedName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countryName', django_countries.fields.CountryField(default='NL', help_text='The two-character country name in ISO 3166 format.', max_length=2, verbose_name='Country Name')),
                ('stateOrProvinceName', models.CharField(default='Noord Holland', help_text="The state/region where your organization is located. This shouldn't be abbreviated. (1–128 characters)", max_length=128, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='State or Province Name')),
                ('localityName', models.CharField(default='Amstelveen', help_text='The city where your organization is located. (1–128 characters)', max_length=128, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Locality Name')),
                ('organizationName', models.CharField(default='Repleo', help_text='The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.', max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Name')),
                ('organizationalUnitName', models.CharField(default='IT Department', help_text='The division of your organization handling the certificate.', max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Unit Name')),
                ('emailAddress', models.EmailField(default='ca@repleo.nl', help_text='The email address to contact your organization. Also used by BounCA for authentication.', max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Email Address')),
                ('commonName', models.CharField(help_text='The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.', max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Common Name')),
                ('subjectAltNames', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')]), blank=True, help_text='subjectAltName list, i.e. dns names for server certs and email adresses for client certs. (separate by comma)', null=True, size=None)),
            ],
            options={
                'db_table': 'bounca_distinguished_name',
            },
        ),
        migrations.AddField(
            model_name='certificate',
            name='dn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='x509_pki.DistinguishedName'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='certificate',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='The signing authority (None for root certificate)', null=True, on_delete=django.db.models.deletion.CASCADE, to='x509_pki.Certificate'),
        ),
        migrations.AlterUniqueTogether(
            name='certificate',
            unique_together=set([('shortname', 'type', 'revoked_uuid'), ('dn', 'type', 'revoked_uuid')]),
        ),
    ]