var matomatControllers = angular.module('matomatControllers', []);

matomatControllers.controller('loginCtrl', ['$scope', '$rootScope',
		function ($scope,$rootScope) {
		$scope.setUser=function (user,pass) {
			$rootScope.user=user;
			$rootScope.pass=pass;
		}
}]);

matomatControllers.controller('detailCtrl', ['$scope', '$http', '$rootScope', '$location',
		function($scope,$http, $rootScope, $location) {
			$scope.loadDetails=function(){
				var url="/api/"+$rootScope.user+"/details";
				$http.get(url,{headers:{pass:$rootScope.pass}})
					.success(function(data){
						$scope.details=data;
					})
					.error(function(data){
						$location.path('/login');
					}
					);
			}

			$scope.loadDetails();
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

			$scope.undo=function(){
				var url="/api/"+$rootScope.user+"/undo";
				$http.post(url,"",{headers:{pass:$rootScope.pass}})
				.success(function(data){
					$scope.message="letzte Aktion r&uuml;ckg&auml;ngig gemacht";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="letzte Aktion konnte nicht r&uuml;ckg&auml;ngig gemacht werden";
				});
			};

			$scope.buy=function(item){
				var url="/api/"+$rootScope.user+"/buy";
				$http.post(url,item,{headers:{pass:$rootScope.pass}})
				.success(function(data){
					$scope.loadBalance();
					for (i in $scope.items){
						it=$scope.items[i];
						if (it.id==item){
							$scope.message="Ein "+it.name+" f&uuml;r (WTF AngularJS) "+it.price/100+"EUR gekauft";
							break;
						}
					}
				})
				.error(function(data){
					$scope.message="Kauf fehlgeschlagen";
				});
			};

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

			$http.get("/api/items")
				.success(function(data){
					$scope.items=data;
				});
			$scope.loadBalance();
		}]);
