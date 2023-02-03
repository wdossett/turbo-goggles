"""
Model exported as python.
Name : model
Group : 
With QGIS : 32800
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
import processing


class Model(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('warehouses', 'Warehouses', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('delivery_sites', 'Delivery Sites', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('warehouse_name', 'Warehouse Name', type=QgsProcessingParameterField.Any, parentLayerParameterName='warehouses', allowMultiple=False, defaultValue='NVILLAGE'))
        self.addParameter(QgsProcessingParameterField('site_warehouse', 'Site Warehouse', type=QgsProcessingParameterField.Any, parentLayerParameterName='delivery_sites', allowMultiple=False, defaultValue='Warehouse'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Split vector layer
        alg_params = {
            'FIELD': parameters['warehouse_name'],
            'FILE_TYPE': 0,  # gpkg
            'INPUT': parameters['warehouses'],
            'PREFIX_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SplitVectorLayer'] = processing.run('native:splitvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Split sites
        alg_params = {
            'FIELD': parameters['site_warehouse'],
            'FILE_TYPE': 0,  # gpkg
            'INPUT': parameters['delivery_sites'],
            'PREFIX_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SplitSites'] = processing.run('native:splitvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Matrix from layers
        alg_params = {
            'INPUT_END_FIELD': '',
            'INPUT_END_LAYER': outputs['SplitSites']['OUTPUT'],
            'INPUT_PROFILE': 0,  # driving-car
            'INPUT_PROVIDER': 0,  # openrouteservice
            'INPUT_START_FIELD': '',
            'INPUT_START_LAYER': outputs['SplitVectorLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MatrixFromLayers'] = processing.run('ORS Tools:matrix_from_layers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'model'

    def displayName(self):
        return 'model'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Model()
