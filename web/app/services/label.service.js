(function () {

  angular.module('glyphMinerApp.core').factory('LabelService', LabelService);

  LabelService.$inject = ['$http', 'apiBasePath', 'ErrorService'];

  function LabelService($http, apiBasePath, ErrorService) {
    var service = {
      postLabel : postLabel,
      putModel  : putModel,
      putSelect : putSelect
    };

    return service;

    ////////////////

    function postLabel(match, label) {
      return $http.post(apiBasePath + '/images/' + match.image_id + '/templates/' + match.template_id + '/matches/' + match.id + '/label', label)
        .then(getComplete)
	 .catch(error => errorHandler(error, {
      imageId: match.image_id,
      templateId: match.template_id,
      matchId: match.id
    }));
    }

    function putModel(imageId, templateId, model) {
      return $http.put(apiBasePath + '/images/' + imageId + '/templates/' + templateId + '/model', model)
        .then(getComplete)
        .catch(errorHandler);
    }

    function putSelect(match, select) {
      return $http.put(apiBasePath + '/images/' + match.image_id + '/templates/' + match.template_id + '/matches/' + match.id + '/select', select)
        .then(getComplete)
        .catch(errorHandler);
    }

    function getComplete(response) {
      return response.data;
    }

    function errorHandler(error, context = {}) {
  const details = [];

  if (context.imageId) details.push(`imageId=${context.imageId}`);
  if (context.templateId) details.push(`templateId=${context.templateId}`);
  if (context.matchId) details.push(`matchId=${context.matchId}`);
  if (error.config && error.config.url) details.push(`url=${error.config.url}`);

  const detailMsg = details.length > 0 ? " [" + details.join(", ") + "]" : "";

  ErrorService.alert(
    "The Label Service encountered an error while trying to access the API (" +
    error.statusText + "). Make sure the server is running and accessible." + detailMsg,
    error.data
  );
}

  }

}());
