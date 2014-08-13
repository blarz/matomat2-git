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
      when('/user', {
        templateUrl: 'partials/user.html',
        controller: 'userCtrl'
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

matomatApp.service('authenticator',['$location','$http','$log', function($location,$http,$log){
	this.user='';
	this.pass='';
	this.login_if_invalid = function() {
		$log.debug(this.user+":"+this.pass);
		var url="/api/"+this.user+"/balance";
		$http.get(url,{headers:{pass:this.pass}})
			.error(function(data,response){
				if (response==403){
					$location.path('/login');
				}
			});
		}
}]);
