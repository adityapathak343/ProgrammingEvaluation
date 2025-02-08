/*
Computer Architecture Lab Test
9/11/2024

Nishit Soni
2021A7PS0672P
*/

module SEQ_DET(z1, x, clk, rst);
	input x, clk, rst;
	output z1;
	
	reg [2:0] state;
	reg z1;
	
	always @(posedge clk, posedge rst)
	begin
		if(rst) begin
			state <= 3'b000;
			z1 <= 0;
		end
		else
		begin
			case(state)
				3'b000: 
				begin
					if(x)
					begin
						state <= 3'b001;
						z1 <= 0;
					end
					else
					begin
						state <= 3'b000;
						z1 <= 0;
					end
				end
				
				3'b001:
				begin
					if(x)
					begin
						state <= 3'b001;
						z1 <= 0;
					end
					else
					begin
						state <= 3'b010;
						z1 <= 0;
					end
				end
				
				3'b010:
				begin
					if(x)
					begin
						state <= 3'b001;
						z1 <= 0;
					end
					else
					begin
						state <= 3'b011;
						z1 <= 0;
					end
				end
				
				3'b011:
				begin
					if(x)
					begin
						state <= 3'b100;
						z1 <= 1;
					end
					else
					begin
						state <= 3'b000;
						z1 <= 0;
					end
				end
				
				3'b100:
				begin
					if(x)
					begin
						state <= 3'b001;
						z1 <= 0;
					end
					else
					begin
						state <= 3'b010;
						z1 <= 0;
					end
				end
				
				default:
				begin
					state <= 3'b000;
					z1 <= 0;
				end
			endcase
		end
	end
endmodule

module BIN_Counter(Q_out, clr1, clr2, clk);
	output [2:0] Q_out;
	input clr1, clr2, clk;
	
	reg [2:0] Q_out;
	
	always @(posedge clk) begin
		if(clr1 | clr2) begin
			Q_out = 0;
		end
		else
		begin
			if(Q_out == 7) begin
				Q_out = 7;
			end
			else 
			begin
				Q_out = Q_out + 1;
			end
		end
	end
endmodule;

module DEC_8(O_8, S_3);
	output [7:0] O_8;
	input [2:0] S_3;
	
	reg [7:0] O_8;
	
	always @(*) begin
		case(S_3)
		3'b000: O_8 <= 8'b00000001;
		3'b001: O_8 <= 8'b00000010;
		3'b010: O_8 <= 8'b00000100;
		3'b011: O_8 <= 8'b00001000;
		3'b100: O_8 <= 8'b00010000;
		3'b101: O_8 <= 8'b00100000;
		3'b110: O_8 <= 8'b01000000;
		3'b111: O_8 <= 8'b10000000;
		endcase
	end
endmodule;

module INTG(z2, z1, x, clk , reset);
	output z2, z1;
	input x, reset, clk;
	
	reg z2;
	reg z1;
	reg [2:0] cnt_out;
	reg [7:0] dec_out
	
	SEQ_DET(z1, x, clk, reset);
	
	BIN_Counter(cnt_out, reset, z2, clk);
	
	DEC_8(dec_out, cnt_out);
	
	assign z2 = dec_out[3];
	
endmodule;

module TESTBENCH;

	reg reset, clk;
	reg [24:0] input_string;
	wire z2, z1, x;
	integer i;	
	
	INTG(z2, z1, x, clk, reset);
	
	initial 
	begin
	clk = 0;
	reset = 1;
	input_string = 25'b1001001100100001001001001;
	#5 reset = 0;
	
	for(i = 0; i < 25; i = i+1) begin: test_loop
	x = input_string[i];
	#2 clk = 1;
	#2 clk = 0;
	
	$display("Outputs: z1 = %b, z2 = %b || inputs x = %b", z1, z2, x);
	end
	
endmodule