function [ prec, recall ] = temporalClusterPRCurve( mapping, rankList, groundTruth )
% Calculte the precision-recall (PR) curve for a rankList of cluster.
% Given a rankList of retrieved cluster {C_i} and a set ofground truth
% communities {C*_j}, calculate the precision and recall of nodes for top i
% clusters with the formula
%   tp_i        = union(C_1, ... C_i)\cap union(C*_{mapping(1)},..., C*_{mapping(i)})   (1)
%   prec_i      = tp_i/sum_{k=1}^i|C_k|         (2)
%   recall_i    = tp_i/sum_{j=1}^J(|C*_j|)     (3)
% The PR curve is then generated by point (prec_i, recall_i) for i=1:I
% Input
%   - mapping:      array, mapping(i) = j means C_i is mapped to C*_j
%   - rankList.clusters:     I*1 cells, rankList.clusters{i} contains the node IDs in C_i
%   - groundTruth:  J*1 cells, store info of each ground truth of component
%       - groundTruth{j}.idx:  array, node ID in community C*_j
%   Detailed explanation goes here
    
%   Initialization
    I = length(mapping);
    J = length(groundTruth);
    prec = zeros(I,1);
    retrievedNum = zeros(I, 1); % sum_{k=1}^i|C_k|
    totalGTNum = 0;             % sum_{j=1}^J(|C*_j|) 
    for j = 1:J
       totalGTNum = totalGTNum + length(groundTruth{j}.idx); 
    end
    for i = 1:I
        if mapping(i) == -1;
            prec(i) = 0;
            retrievedNum(i) = 0; 
        else
            prec(i) = length(intersect(rankList.clusters{i}, groundTruth{mapping(i)}.idx)); 
            retrievedNum(i) = length(rankList.clusters{i});
        end
    end
    prec = cumsum(prec(1:I));
    retrievedNum = cumsum(retrievedNum(1:I));
    recall = [0; prec / totalGTNum];
    prec = [0; prec ./ retrievedNum];
    
    % if recall(end) < 1
    %    recall(end+1) = recall(end) ;
    %    prec(end +1) = retrievedNum(end)/totalGTNum;
    %    recall(end+1) = 1;
    %    prec(end +1) = prec(end);
    % end
    prec(recall==0)=0;
end

