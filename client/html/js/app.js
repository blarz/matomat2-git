var matomatApp = angular.module('matomatApp', [
		'ngRoute',
		'matomatControllers'
		]);

matomatApp.config(['$routeProvider','$sceProvider',
  function($routeProvider,$sceProvider) {
    //$sceProvider.enabled(false);
    $routeProvider.
      when('/login', {
        templateUrl: 'partials/login.html',
        controller: 'loginCtrl'
      }).
      when('/balance', {
        templateUrl: 'partials/balance.html',
        controller: 'balanceCtrl'
      }).
      when('/details', {
        templateUrl: 'partials/details.html',
        controller: 'detailCtrl'
      }).
      otherwise({
        redirectTo: '/login'
      });
  }]);
