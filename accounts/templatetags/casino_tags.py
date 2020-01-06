'''
Created on Oct 24, 2011

@author: tvassila
'''
import time
#===============================================================================
# import copy
# from django.template import TemplateSyntaxError, Node, Variable, Library
# from django.utils.datastructures import SortedDict
#===============================================================================

from django.template import Library
from cancan import settings
register = Library()


    
@register.simple_tag(takes_context=True)
def get_settings(context, key):
    context[key] = getattr(settings, key,'COuKOU-%s' % key)
    return ''

@register.filter
def split(str):
    return str.split(",")

@register.simple_tag
def test_tag():
    return "<span>" + "</span><span>".join(["one", "two", "three"])+"</span>"


#===============================================================================
# def get_fieldset(parser, token):
#    try:
#        name, fields, as_, variable_name, from_, form = token.split_contents()
#    except ValueError:
#        raise TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])
#    return FieldSetNode(fields.split(','), variable_name, form)
# 
# get_fieldset = register.tag(get_fieldset)
# 
# class FieldSetNode(Node):
#    def __init__(self, fields, variable_name, form_variable):
#        print fields
#        print 'form.fields', form_variable.fields
#        self.fields = fields
#        self.variable_name = variable_name
#        self.form_variable = form_variable
# 
#    def render(self, context):
#        form = Variable(self.form_variable).resolve(context)
#        new_form = copy.copy(form)        
#        new_form.fields = SortedDict([(key, form.fields[key]) for key in self.fields])
#        context[self.variable_name] = new_form
#        return u'' 
#===============================================================================