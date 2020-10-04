#include<bits/stdc++.h>
using namespace std;
#define ll long long int
ll gcd( ll a, ll b )
{
  if( b == 0 )
    return a;
  
  else
    return gcd( b, a%b );
}

ll reduceB(ll a, string b) 
{ 
    ll mod = 0; 
    for (int i=0; i<b.size(); i++) 
        mod = (mod*10 + b[i] - '0')%a; 
  
    return mod;
} 

ll gcdLarge(ll a, string b) 
{ 
    ll num = reduceB(a, b); 
    
    return gcd(a, num); 
} 

int main()
{
  int t;
  cin >> t;
  while( t-- )
  {
    ll a;
    cin >> a;
    string b;
    cin >> b;
    if (a == 0) 
        cout << b << endl; 
    else
        cout << gcdLarge(a, b) << endl; 
  }
}
