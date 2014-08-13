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
					.error(function(data,response){
						if (response==403){
							$location.path('/login');
						}
					}
					);
			}

}]);

matomatControllers.controller('userCtrl', ['$scope', '$http', '$rootScope', '$location',
		function($scope,$http, $rootScope, $location) {
			$scope.new_user=$rootScope.user;

			$scope.loadBalance=function(){
				var url="/api/"+$rootScope.user+"/balance";
				$http.get(url,{headers:{pass:$rootScope.pass}})
					.error(function(data,response){
						if (response==403){
							$location.path('/login');
						}
					}
					);
			}
			$scope.loadBalance(); // check authentication

			$scope.create_user=function(){
				if ($scope.pass1!=$scope.pass2){
					$scope.message="Zweiteingabe des Passwortes stimmt nicht";
					return;
				}
				var url="/api/"+$rootScope.user+"/user";
				var data={"username":$scope.new_user,"password":$scope.pass1};
				$http.post(url,data,{headers:{pass:$rootScope.pass}})
				.success(function(data){
					$scope.message="Benutzer angelegt";
				})
				.error(function(data){
					$scope.message="Benutzer konnte nicht angelegt werden";
				});
			}
}]);

matomatControllers.controller('balanceCtrl', ['$scope', '$http', '$rootScope', '$location', '$log',
		function($scope,$http, $rootScope, $location, $log) {
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
					.error(function(data,response){
						if (response==403){
							$location.path('/login');
						}
					}
					);
			}

			$http.get("/api/items")
				.success(function(data){
					$scope.items=data;
				});
			$scope.loadBalance();
		}]);
