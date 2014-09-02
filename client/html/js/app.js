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
      when('/items', {
        templateUrl: 'partials/items.html',
        controller: 'itemsCtrl'
      }).
      otherwise({
        redirectTo: '/login'
      });
  }]);

matomatApp.service('authenticator',['$location','$http','$log','$window','$rootScope', function($location,$http,$log,$window,$rootScope){
	this.user=$window.localStorage['matomat_user'];
	this.pass=$window.localStorage['matomat_pass'];
	if (this.user){
		this.remembered=true;
	}
	this.user=this.user?this.user:'';
	this.pass=this.pass?this.pass:'';

	this.remember = function(){
		$window.localStorage['matomat_user']=this.user;
		$window.localStorage['matomat_pass']=this.pass;
		this.remembered=true;
	};
	this.forget = function(){
		$window.localStorage.removeItem('matomat_user');
		$window.localStorage.removeItem('matomat_pass');
		this.remembered=false;
		this.user='';
		this.pass='';
	};
	var me=this;
	$rootScope.forget = function(){
			me.forget();
	};
	this.login_if_invalid = function() {
		var url="api/"+this.user+"/user";
		auth=this;
		$http.get(url,{headers:{pass:this.pass}})
			.success(function(data,response){
				auth.user=data.username;
			})
			.error(function(data,response){
				if (response==403){
					auth.forget();
					$location.path('/login');
				}
			});
		};
	this.forward_if_valid = function(target) {
		var url="api/"+this.user+"/user";
		auth=this;
		$http.get(url,{headers:{pass:this.pass}})
			.success(function(data,response){
				auth.user=data.username;
				$location.path(target).replace();
			});
		};
}]);
