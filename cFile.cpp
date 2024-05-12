#include <iostream>
#include <fstream>
#include <cstring>
#include <string>

#define STATES  99
#define SYMBOLS 20

using namespace std;

int N_symbols;
int N_DFA_states;   
char* DFA_finals;   
int DFAtab[STATES][SYMBOLS];

char StateName[STATES][STATES + 1];   

int N_optDFA_states;    
int OptDFA[STATES][SYMBOLS];
char NEW_finals[STATES + 1];


void saveinFile(int tab[][SYMBOLS], int nstates, int nsymbols, const char* finals){
	int i, j;
	ofstream output("output.txt");
	output<<nstates<<" "<<nsymbols<<endl;
	output<<finals<<endl;
    for (i = 0; i < nstates; i++) {
        for (j = 0; j < nsymbols; j++)
            output << char(tab[i][j]);
        output << "\n";
    }
}




void load_DFA_table(){

	ifstream input("input.txt");
	string finals;
	int states;
	int symbols;
	
	input>>states>>symbols;
	input>>finals;

	
	N_DFA_states=states;
	N_symbols=symbols;	
    DFA_finals = new char[finals.length() + 1];
    strcpy(DFA_finals, finals.c_str()); 

	string temp;
	int i=0;
	if (input.is_open()) {
	     while (input.good()) {
			input>> temp;
		//	cout<<temp<<endl;;
				for(int j=0;j<temp.length();j++){
					DFAtab[i][j]=temp[j];
				}
			i++;	
			}  
	}
}

void get_next_state(char* nextstates, char* cur_states,
    int dfa[STATES][SYMBOLS], int symbol){
    int i, ch;

    for (i = 0; i < strlen(cur_states); i++)
        *nextstates++ = dfa[cur_states[i] - 'A'][symbol];
    *nextstates = '\0';
}

char equiv_class_ndx(char ch, char stnt[][STATES + 1], int n){
    int i;

    for (i = 0; i < n; i++)
        if (strchr(stnt[i], ch)) return i + '0';
    return -1;  
}

char is_one_nextstate(char* s)
{
    char equiv_class;   

    while (*s == '@') s++;
    equiv_class = *s++; 

    while (*s) {
        if (*s != '@' && *s != equiv_class) return 0;
        s++;
    }

    return equiv_class;
}

int state_index(char* state, char stnt[][STATES + 1], int n, int* pn, int cur){
    int i;
    char state_flags[STATES + 1]; 

    if (!*state) return -1; 

    for (i = 0; i < strlen(state); i++)
        state_flags[i] = equiv_class_ndx(state[i], stnt, n);
    state_flags[i] = '\0';

    if (i = is_one_nextstate(state_flags))
        return i - '0';   
    else {
        strcpy(stnt[*pn], state_flags); 
        return (*pn)++;
    }
}

int init_equiv_class(char statename[][STATES + 1], int n, const char* finals){
    int i, j;

    if (strlen(finals) == n) {  
        strcpy(statename[0], finals);
        return 1;
    }

    strcpy(statename[1], finals);   

    for (i = j = 0; i < n; i++) {
        if (i == *finals - 'A') {
            finals++;
        }
        else statename[0][j++] = i + 'A';
    }
    statename[0][j] = '\0';

    return 2;
}

int get_optimized_DFA(char stnt[][STATES + 1], int n,
    int dfa[][SYMBOLS], int n_sym, int newdfa[][SYMBOLS]){
    int n2 = n;       
    int i, j;
    char nextstate[STATES + 1];

    for (i = 0; i < n; i++) { 
        for (j = 0; j < n_sym; j++) {  
            get_next_state(nextstate, stnt[i], dfa, j);
            newdfa[i][j] = state_index(nextstate, stnt, n, &n2, i) + 'A';
        }
    }

    return n2;
}

void chr_append(char* s, char ch){
    int n = strlen(s);

    *(s + n) = ch;
    *(s + n + 1) = '\0';
}

void sort(char stnt[][STATES + 1], int n){
    int i, j;
    char temp[STATES + 1];

    for (i = 0; i < n - 1; i++)
        for (j = i + 1; j < n; j++)
            if (stnt[i][0] > stnt[j][0]) {
                strcpy(temp, stnt[i]);
                strcpy(stnt[i], stnt[j]);
                strcpy(stnt[j], temp);
            }
}

int split_equiv_class(char stnt[][STATES + 1], int i1, int i2, int n, int n_dfa){
    char* old = stnt[i1], * vec = stnt[i2];
    int i, n2, flag = 0;
    char newstates[STATES][STATES + 1];   

    for (i = 0; i < STATES; i++) newstates[i][0] = '\0';

    for (i = 0; vec[i]; i++)
        chr_append(newstates[vec[i] - '0'], old[i]);

    for (i = 0, n2 = n; i < n_dfa; i++) {
        if (newstates[i][0]) {
            if (!flag) {    
                strcpy(stnt[i1], newstates[i]);
                flag = 1;   
            }
            else  
                strcpy(stnt[n2++], newstates[i]);
        }
    }

    sort(stnt, n2);

    return n2; 
}

int set_new_equiv_class(char stnt[][STATES + 1], int n, int newdfa[][SYMBOLS], int n_sym, int n_dfa){
    int i, j, k;

    for (i = 0; i < n; i++) {
        for (j = 0; j < n_sym; j++) {
            k = newdfa[i][j] - 'A';   
            if (k >= n)  
                return split_equiv_class(stnt, i, k, n, n_dfa);
        }
    }

    return n;
}

int optimize_DFA(int dfa[][SYMBOLS], int n_dfa, int n_sym, const char* finals, char stnt[][STATES + 1], int newdfa[][SYMBOLS]){
    char nextstate[STATES + 1];
    int n;  
    int n2; 

    n = init_equiv_class(stnt, n_dfa, finals);

    while (1) {
        n2 = get_optimized_DFA(stnt, n, dfa, n_sym, newdfa);
        if (n != n2)
            n = set_new_equiv_class(stnt, n, newdfa, n_sym, n_dfa);
        else break; 
    }

    return n;   
}

int is_subset(const char* s, const char* t){
    int i;

    for (i = 0; *t; i++)
        if (!strchr(s, *t++)) return 0;
    return 1;
}


void get_NEW_finals(char* newfinals, const char* oldfinals, char stnt[][STATES + 1], int n){
    int i;

    for (i = 0; i < n; i++)
        if (is_subset(oldfinals, stnt[i])) *newfinals++ = i + 'A';
    *newfinals++ = '\0';
}

int main(){
    load_DFA_table();
    //print_dfa_table(DFAtab, N_DFA_states, N_symbols, DFA_finals);

    N_optDFA_states = optimize_DFA(DFAtab, N_DFA_states,
        N_symbols, DFA_finals, StateName, OptDFA);
    get_NEW_finals(NEW_finals, DFA_finals, StateName, N_optDFA_states);

   // print_dfa_table(OptDFA, N_optDFA_states, N_symbols, NEW_finals);
    saveinFile(OptDFA, N_optDFA_states, N_symbols, NEW_finals);
int k;
cout<<"Just checking if its running.\n";
//	cin>>k;
    return 0;
}