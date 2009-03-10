import unittest

from StringIO import StringIO
from elementtree import ElementTree

from zope.interface import alsoProvides
from zope.component import provideUtility
from zope.component.testing import tearDown

from zope.configuration import xmlconfig

from plone.registry.interfaces import IRegistry, IInterfaceAwareRecord
from plone.registry import Record, field

from plone.app.registry import Registry

from plone.app.registry.exportimport.handler import import_registry, export_registry

from plone.supermodel.utils import pretty_xml

from Products.GenericSetup.tests.common import DummyImportContext
from Products.GenericSetup.tests.common import DummyExportContext

from OFS.ObjectManager import ObjectManager

from plone.app.registry.tests import data

configuration = """\
<configure xmlns="http://namespaces.zope.org/zope">     
    <include package="zope.component" file="meta.zcml" />
    <include package="zope.app.component" file="meta.zcml" />
    <include package="plone.registry" />
    <include package="plone.app.registry.exportimport" file="handlers.zcml" />
</configure>
"""


class ExportImportTest(unittest.TestCase):
    
    def setUp(self):        
        self.site = ObjectManager('plone')
        self.registry = Registry('portal_registry')
        provideUtility(provides=IRegistry, component=self.registry)
        xmlconfig.xmlconfig(StringIO(configuration))

    def tearDown(self):
        tearDown()
        
    def assertXmlEquals(self, expected, actual):
        
        expected_tree = ElementTree.XML(expected)
        actual_tree = ElementTree.XML(actual)
        
        if ElementTree.tostring(expected_tree) != ElementTree.tostring(actual_tree):
            print
            print "Expected:"
            print pretty_xml(expected_tree)
            print
            
            print
            print "Actual:"
            print pretty_xml(actual_tree)
            print
            
            raise AssertionError(u"XML mis-match")
            

class TestImport(ExportImportTest):

    def test_empty_import_no_purge(self):
        
        xml = "<registry/>"
        context = DummyImportContext(self.site, purge=False)
        context._files = {'registry.xml': xml}
        
        self.registry.records['test.export.simple'] = \
            Record(field.TextLine(title=u"Simple record", default=u"N/A"),
                   value=u"Sample value")
        import_registry(context)
        
        self.assertEquals(1, len(self.registry.records))

    def test_import_purge(self):
        
        xml = "<registry/>"
        context = DummyImportContext(self.site, purge=True)
        context._files = {'registry.xml': xml}
        
        self.registry.records['test.export.simple'] = \
            Record(field.TextLine(title=u"Simple record", default=u"N/A"),
                   value=u"Sample value")
        import_registry(context)
        
        self.assertEquals(0, len(self.registry.records))
        
    def test_import_records(self):
        pass
        
    def test_import_records_disallowed(self):
        pass
        
    def test_import_records_omit(self):
        pass
        
    def test_import_value_only(self):
        pass
        
    def test_import_interface(self):
        pass
        
    def test_import_field_only(self):
        pass
    
    def test_import_field_and_interface(self):
        pass
        
    def test_import_collection_field(self):
        pass
        
    def test_import_dict_field(self):
        pass
        
    def test_import_choice_field(self):
        pass
        
    def test_import_list_value(self):
        pass

class TestExport(ExportImportTest):
    
    def test_export_empty(self):
        
        xml = """<registry />"""
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

    def test_export_simple(self):
        
        xml = """\
<registry>
  <record name="test.export.simple">
    <field type="plone.registry.field.TextLine">
      <default>N/A</default>
      <title>Simple record</title>
    </field>
    <value>Sample value</value>
  </record>
</registry>"""
        
        self.registry.records['test.export.simple'] = \
            Record(field.TextLine(title=u"Simple record", default=u"N/A"),
                   value=u"Sample value")
        
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

    def test_export_with_interface(self):
        xml = """\
<registry>
  <record field="age" interface="plone.app.registry.tests.data.ITestSettings" name="plone.app.registry.tests.data.ITestSettings.age">
    <field type="plone.registry.field.Int">
      <min>0</min>
      <title>Age</title>
    </field>
    <value />
  </record>
  <record field="name" interface="plone.app.registry.tests.data.ITestSettings" name="plone.app.registry.tests.data.ITestSettings.name">
    <field type="plone.registry.field.TextLine">
      <default>Mr. Registry</default>
      <title>Name</title>
    </field>
    <value>Mr. Registry</value>
  </record>
  <record name="test.export.simple">
    <field type="plone.registry.field.TextLine">
      <default>N/A</default>
      <title>Simple record</title>
    </field>
    <value>Sample value</value>
  </record>
</registry>"""
        
        self.registry.records['test.export.simple'] = \
            Record(field.TextLine(title=u"Simple record", default=u"N/A"),
                   value=u"Sample value")
        
        self.registry.register_interface(data.ITestSettings)
                   
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])
        
    def test_export_with_collection(self):
        
        xml = """\
<registry>
  <record name="test.export.simple">
    <field type="plone.registry.field.List">
      <title>Simple record</title>
      <value_type type="plone.registry.field.Int">
        <title>Val</title>
      </value_type>
    </field>
    <value>
      <element>2</element>
    </value>
  </record>
</registry>"""
        self.registry.records['test.export.simple'] = \
            Record(field.List(title=u"Simple record", value_type=field.Int(title=u"Val")),
                   value=[2])
        
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

    def test_export_with_dict(self):
        
        xml = """\
<registry>
  <record name="test.export.dict">
    <field type="plone.registry.field.Dict">
      <default />
      <key_type type="plone.registry.field.ASCIILine">
        <title>Key</title>
      </key_type>
      <title>Dict</title>
      <value_type type="plone.registry.field.Int">
        <title>Value</title>
      </value_type>
    </field>
    <value>
      <element key="a">1</element>
    </value>
  </record>
</registry>"""
        
        self.registry.records['test.export.dict'] = \
            Record(field.Dict(title=u"Dict", default={},
                              key_type=field.ASCIILine(title=u"Key"),
                              value_type=field.Int(title=u"Value")),
                   value={'a': 1})
        
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

    def test_export_with_choice(self):
        xml = """\
<registry>
  <record name="test.export.choice">
    <field type="plone.registry.field.Choice">
      <title>Simple record</title>
      <vocabulary>dummy.vocab</vocabulary>
    </field>
    <value />
  </record>
</registry>"""
        
        self.registry.records['test.export.choice'] = \
            Record(field.Choice(title=u"Simple record", vocabulary=u"dummy.vocab"))
        
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

    def test_export_with_missing_schema_does_not_error(self):
        xml = """\
<registry>
  <record field="blah" interface="non.existant.ISchema" name="test.export.simple">
    <field type="plone.registry.field.TextLine">
      <default>N/A</default>
      <title>Simple record</title>
    </field>
    <value>Sample value</value>
  </record>
</registry>"""
        
        self.registry.records['test.export.simple'] = \
            Record(field.TextLine(title=u"Simple record", default=u"N/A"),
                   value=u"Sample value")
        self.registry.records['test.export.simple'].interface_name = 'non.existant.ISchema'
        self.registry.records['test.export.simple'].field_name = 'blah'
        
        alsoProvides(self.registry.records['test.export.simple'], IInterfaceAwareRecord)
        
        context = DummyExportContext(self.site)
        export_registry(context)
        
        self.assertEquals('registry.xml', context._wrote[0][0])
        self.assertXmlEquals(xml, context._wrote[0][1])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImport))
    suite.addTest(unittest.makeSuite(TestExport))
    return suite