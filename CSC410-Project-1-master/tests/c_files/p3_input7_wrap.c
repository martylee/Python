void main(){
	for(i=0;i<n;i++){
	   if(i>n/2){
	      hist = hist - a[i];
	   } else {
	     hist = hist + a[i];
	   }
	   b = b && hist > 0;
	}
	f = b ? hist : 0;}
