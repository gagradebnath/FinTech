const { ethers } = require("hardhat");

async function main() {
    console.log("🚀 Deploying FinGuard Smart Contracts...");
    
    // Get deployer account
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());
    
    // Deploy FinGuardToken
    console.log("\n📝 Deploying FinGuardToken...");
    const FinGuardToken = await ethers.getContractFactory("FinGuardToken");
    const finguardToken = await FinGuardToken.deploy(
        "FinGuard Token",
        "FGT",
        18, // decimals
        ethers.utils.parseEther("1000000") // 1 million initial supply
    );
    await finguardToken.deployed();
    console.log("✅ FinGuardToken deployed to:", finguardToken.address);
    
    // Deploy TransactionManager
    console.log("\n📝 Deploying TransactionManager...");
    const TransactionManager = await ethers.getContractFactory("TransactionManager");
    const transactionManager = await TransactionManager.deploy(finguardToken.address);
    await transactionManager.deployed();
    console.log("✅ TransactionManager deployed to:", transactionManager.address);
    
    // Deploy BudgetManager
    console.log("\n📝 Deploying BudgetManager...");
    const BudgetManager = await ethers.getContractFactory("BudgetManager");
    const budgetManager = await BudgetManager.deploy(finguardToken.address);
    await budgetManager.deployed();
    console.log("✅ BudgetManager deployed to:", budgetManager.address);
    
    // Authorize TransactionManager to mint tokens
    console.log("\n🔐 Setting up permissions...");
    await finguardToken.authorizeMinter(transactionManager.address);
    console.log("✅ TransactionManager authorized to mint tokens");
    
    // Create some test accounts and distribute tokens
    console.log("\n👥 Setting up test accounts...");
    const accounts = await ethers.getSigners();
    
    // Transfer tokens to test accounts
    for (let i = 1; i < Math.min(6, accounts.length); i++) {
        const amount = ethers.utils.parseEther("10000"); // 10,000 tokens each
        await finguardToken.transfer(accounts[i].address, amount);
        console.log(`✅ Transferred ${ethers.utils.formatEther(amount)} FGT to ${accounts[i].address}`);
    }
    
    // Register test users in TransactionManager
    const userIds = ["admin", "admin2", "admin3", "admin4", "admin5"];
    for (let i = 1; i < Math.min(6, accounts.length); i++) {
        await transactionManager.registerUser(
            userIds[i-1],
            accounts[i].address,
            ethers.utils.parseEther("5000"), // 5,000 daily limit
            i === 1 // First user is an agent
        );
        console.log(`✅ Registered user ${userIds[i-1]} at ${accounts[i].address}`);
    }
    
    // Create test budgets
    console.log("\n💰 Creating test budgets...");
    const budgetCategories = ["Food", "Transportation", "Entertainment", "Shopping"];
    for (let i = 1; i < Math.min(5, accounts.length); i++) {
        const category = budgetCategories[i-1];
        const amount = ethers.utils.parseEther("1000"); // 1,000 tokens budget
        const duration = 30 * 24 * 60 * 60; // 30 days
        
        await budgetManager.createBudget(
            accounts[i].address,
            category,
            amount,
            duration
        );
        console.log(`✅ Created ${category} budget of ${ethers.utils.formatEther(amount)} FGT for ${accounts[i].address}`);
    }
    
    console.log("\n🎉 Deployment completed successfully!");
    console.log("\n📋 Contract Addresses:");
    console.log("FinGuardToken:", finguardToken.address);
    console.log("TransactionManager:", transactionManager.address);
    console.log("BudgetManager:", budgetManager.address);
    
    console.log("\n💡 Next steps:");
    console.log("1. Update your Python application with these contract addresses");
    console.log("2. Start the Hardhat node: npx hardhat node");
    console.log("3. Run your Flask application with Solidity integration");
    
    // Save deployment info to file
    const deploymentInfo = {
        network: "hardhat",
        deployer: deployer.address,
        contracts: {
            FinGuardToken: finguardToken.address,
            TransactionManager: transactionManager.address,
            BudgetManager: budgetManager.address
        },
        testAccounts: accounts.slice(1, 6).map((acc, index) => ({
            address: acc.address,
            userId: userIds[index],
            balance: "10000"
        }))
    };
    
    const fs = require('fs');
    fs.writeFileSync(
        './deployment-info.json',
        JSON.stringify(deploymentInfo, null, 2)
    );
    console.log("\n💾 Deployment info saved to deployment-info.json");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });
