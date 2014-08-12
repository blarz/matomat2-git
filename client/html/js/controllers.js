var matomatControllers = angular.module('matomatControllers', []);

matomatControllers.controller('loginCtrl', ['$scope', '$rootScope',
		function ($scope,$rootScope) {
		$scope.setUser=function (user,pass) {
			$rootScope.user=user;
			$rootScope.pass=pass;
		}
}]);

matomatControllers.controller('balanceCtrl', ['$scope', '$http', '$rootScope', '$location',
		function($scope,$http, $rootScope, $location) {
			$scope.pay=function(amount){
				var url="/api/"+$rootScope.user+"/pay";
				$http.post(url,amount*100,{headers:{pass:$rootScope.pass}})
				.success(function(data){
					$scope.message=""+amount+"EUR (Eurozeichen (&euro;) gibts nicht. WTF AngularJS) eingezahlt";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="Einzahlen fehlgeschlagen";
				});
			};
			$http.get("/api/items")
				.success(function(data){
					$scope.items=data;
				});
			$scope.loadBalance=function(){
				var url="/api/"+$rootScope.user+"/balance";
				$http.get(url,{headers:{pass:$rootScope.pass}})
					.success(function(data){
						$scope.balance=data;
					})
					.error(function(data){
						$location.path('/login');
					}
					);
			}
			$scope.loadBalance();
		}]);
