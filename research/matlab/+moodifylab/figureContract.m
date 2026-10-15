function contract = figureContract(figureId, nameValue)
%FIGURECONTRACT Declare the scientific purpose and review boundary of a figure.

arguments
    figureId (1,1) string
    nameValue.Conclusion (1,1) string = "UNDECLARED"
    nameValue.EvidenceRole (1,1) string = "exploratory"
    nameValue.SourceData (1,:) string = strings(1,0)
    nameValue.Units (1,:) string = strings(1,0)
    nameValue.CalibrationStatus (1,1) string = "NOT_APPLICABLE"
    nameValue.Uncertainty (1,1) string = "NOT_REPORTED"
    nameValue.Limitations (1,1) string = "UNDECLARED"
end

contract = struct();
contract.figureId = figureId;
contract.conclusion = nameValue.Conclusion;
contract.evidenceRole = nameValue.EvidenceRole;
contract.sourceData = nameValue.SourceData;
contract.units = nameValue.Units;
contract.calibrationStatus = nameValue.CalibrationStatus;
contract.uncertainty = nameValue.Uncertainty;
contract.limitations = nameValue.Limitations;
end
