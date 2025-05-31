(function () {

  angular.module('glyphMinerApp', [
    /* common core */
    'glyphMinerApp.core',
  
    /* Feature areas */
    'glyphMinerApp.overview',
    'glyphMinerApp.viewer',
    'glyphMinerApp.activeLearner',    
    'glyphMinerApp.glyphs',
    'glyphMinerApp.pageCreator',
    
    /* 3-rd party modules */
    'ui.router',
    'angular.filter'
  ]);
  
  angular.module('glyphMinerApp').run(['$rootScope', '$state', '$stateParams',
    function ($rootScope, $state, $stateParams) {
      $rootScope.$state = $state;
      $rootScope.$stateParams = $stateParams;
      
      // 🚀 Add this: Inject runId from window.RUN_ID (set by backend in index.html)
      $rootScope.runId = window.RUN_ID || "N/A";
    }
  ]);
    
}());
