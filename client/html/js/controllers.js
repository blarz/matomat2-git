var matomatControllers = angular.module('matomatControllers', []);

matomatControllers.controller('loginCtrl', ['$scope','authenticator',
		function ($scope,authenticator) {
		$scope.setUser=function (user,pass) {
			authenticator.user=user;
			authenticator.pass=pass;
		}
}]);

matomatControllers.controller('detailCtrl', ['$scope', '$http', 'authenticator',
		function($scope,$http, authenticator) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.loadDetails=function(){
				var url="/api/"+$scope.user+"/details";
				$http.get(url,{headers:{pass:$scope.pass}})
					.success(function(data){
						$scope.details=data;
					});
			}
			$scope.loadDetails();
}]);

matomatControllers.controller('userCtrl', ['$scope', '$http', 'authenticator',
		function($scope,$http, authenticator) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.new_user=$scope.user;

			$scope.create_user=function(){
				if ($scope.pass1!=$scope.pass2){
					$scope.message="Zweiteingabe des Passwortes stimmt nicht";
					return;
				}
				var url="/api/"+$scope.user+"/user";
				var data={"username":$scope.new_user,"password":$scope.pass1};
				$http.post(url,data,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message="Benutzer angelegt";
				})
				.error(function(data){
					$scope.message="Benutzer konnte nicht angelegt werden";
				});
			}
}]);

matomatControllers.controller('balanceCtrl', ['$scope', '$http', '$location', 'authenticator',
		function($scope,$http,  $location, authenticator) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.pay=function(amount){
				var url="/api/"+$scope.user+"/pay";
				$http.post(url,amount*100,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message=""+amount+"EUR (Eurozeichen (&euro;) gibts nicht. WTF AngularJS) eingezahlt";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="Einzahlen fehlgeschlagen";
				});
			};

			$scope.undo=function(){
				var url="/api/"+$scope.user+"/undo";
				$http.post(url,"",{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message="letzte Aktion r&uuml;ckg&auml;ngig gemacht";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="letzte Aktion konnte nicht r&uuml;ckg&auml;ngig gemacht werden";
				});
			};

			$scope.buy=function(item){
				var url="/api/"+$scope.user+"/buy";
				$http.post(url,item,{headers:{pass:$scope.pass}})
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
				var url="/api/"+$scope.user+"/balance";
				$http.get(url,{headers:{pass:$scope.pass}})
					.success(function(data){
						$scope.balance=data;
					})
					.error(function(data,response){
						$scope.message="Konnte anktuellen Kontostand nicht empfangen";
					}
					);
			}

			$http.get("/api/items")
				.success(function(data){
					$scope.items=data;
				});
			$scope.loadBalance();
		}]);
