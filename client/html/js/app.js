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
      otherwise({
        redirectTo: '/login'
      });
  }]);
